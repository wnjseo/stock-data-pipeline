from datetime import timedelta
import time
import logging
from sqlalchemy import text
import yfinance as yf
import pandas as pd
from db import engine
from config import (
    BACKFILL_START_DATE, MAX_RETRIES, RETRY_DELAY, REQUEST_DELAY,
    INDICATOR_LOOKBACK_DAYS, PRICE_COLUMNS, HISTORY_COLUMNS
)

logger = logging.getLogger(__name__)

def get_active_tickers():
    """
    company 테이블로부터 is_active가 TRUE인 ticker 목록을 조회한다.

    Returns:
        list[str]: 활성화된 S&P 500 티커 목록 
    """
    
    query = text("""
        SELECT ticker 
        FROM company
        WHERE is_active = TRUE;
    """)

    with engine.connect() as conn:
        tickers = conn.execute(query).scalars().all()

    return tickers

def get_last_dates(tickers):
    """
    daily_stock_price 테이블에서 마지막 수집 날짜를 조회한다.

    Args:
        tickers (list[str]): 조회할 티커 목록

    Returns:
        dict[str, date]: 티커를 키로 마지막 수집 날짜를 갖는 딕셔너리
    """

    if not tickers:
        return {}

    query = text("""
        SELECT ticker, MAX(trade_date) AS last_date
        FROM daily_stock_price
        WHERE ticker = ANY(:tickers)
        GROUP BY ticker;
    """)

    with engine.connect() as conn:
        rows = conn.execute(query, {"tickers": tickers}).fetchall()

    last_dates = {
        ticker: last_date for ticker, last_date in rows
    }

    return last_dates

def extract_daily_stock_info(tickers, last_dates):
    """
    yfinance에서 ticker별 OHLCV를 조회한다.

    Args:
        tickers (list[str]): 조회한 S&P 500 티커 목록
        last_dates (dict[str, date]): 티커별 마지막 수집 날짜

    Returns:
        tuple[pd.DataFrame, list[dict]]:
            - 주가 정보 데이터프레임
            - 조회에 실패한 티커의 오류 정보 목록
    """

    daily_ohlcvs = []
    errors = []
    
    for ticker in tickers:
        last_date = last_dates.get(ticker)

        # 최초 수집은 백필, 이후에는 마지막 수집 다음날 부터 증분 조회
        start_date = (
            BACKFILL_START_DATE
            if last_date is None 
            else last_date + timedelta(days=1)
        )

        # 티커 하나당 3번까지 재시도
        for attempt in range(MAX_RETRIES):
            try:
                ohlcv = yf.download(
                    ticker, 
                    start=start_date, 
                    auto_adjust=False, 
                    progress=False
                ).reset_index()

                # yfinance가 빈 DataFrame을 반환한 경우
                if ohlcv.empty:
                    if attempt < MAX_RETRIES-1:
                        time.sleep(RETRY_DELAY)
                        continue
                    logger.warning(
                        "%s: no data returned from yfinance (start=%s)",
                        ticker,
                        start_date
                    )
                    break

                # yfinance가 변환한 MultiIndex 컬럼을 단일 레벨 컬럼으로 변환
                if isinstance(ohlcv.columns, pd.MultiIndex):
                    ohlcv.columns = ohlcv.columns.get_level_values(0)

                ohlcv.insert(0, "ticker", ticker)
                daily_ohlcvs.append(ohlcv)
                break

            except Exception as e:
                if attempt == MAX_RETRIES-1:
                    errors.append({
                        "ticker": ticker,
                        "pipeline_step": "extract",
                        "task_name": "extract_daily_stock_info",
                        "error_type": type(e).__name__,
                        "error_msg": str(e)
                    })
                else:
                    time.sleep(RETRY_DELAY)
        # API 호출 간격을 두어 과도한 요청을 방지한다.
        time.sleep(REQUEST_DELAY)
    
    if not daily_ohlcvs:
        return pd.DataFrame(columns=PRICE_COLUMNS), errors

    return pd.concat(daily_ohlcvs, ignore_index=True), errors

def get_price_history_for_indicator(tickers, days=INDICATOR_LOOKBACK_DAYS):
    """
    증분 적재 시 파생 지표 계산에 필요한 과거 주가 데이터를 조회한다.

    Args:
        tickers (list[str]): 증분 적재할 티커 목록
        days (int): 티커별로 조회할 최근 거래일 수
    
    Returns:
        pd.DataFrame: ticker, trade_date, adj_close_price, volume 컬럼을 가진 데이터프레임
    """

    if not tickers:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    query = text("""
        SELECT ticker, trade_date, adj_close_price, volume
        FROM (
            SELECT ticker, trade_date, adj_close_price, volume, 
            -- 티커별 최근 N개 거래일만 조회
            ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY trade_date DESC) AS rn
            FROM daily_stock_price
            WHERE ticker = ANY(:tickers)
        ) AS t
        WHERE rn <= :days
        ORDER BY ticker, trade_date;
    """)

    with engine.connect() as conn:
        history_df = pd.read_sql(query, conn, params={"tickers": tickers, "days": days})

    return history_df