import logging
import pandas as pd
from extract_stock import get_price_history_for_indicator
from config import PRICE_COLUMNS, INDICATOR_COLUMNS, HISTORY_COLUMNS, INDICATOR_LOOKBACK_DAYS

def transform_daily_stock_price(raw_stock_df):
    """
    원본 OHLCV를 daily_stock_price 테이블 형식으로 변환한다.

    Args:
        raw_stock_df (pd.DataFrame): 원본 주가 정보 데이터프레임
    
    Returns:
        pd.DataFrame: daily_stock_price 적재용 데이터프레임 (ticker, trade_date, OHLCV)
    """

    # 변환할 데이터가 없으면 빈 데이터프레임 반환
    if raw_stock_df.empty:
        return pd.DataFrame(columns=PRICE_COLUMNS)

    df = raw_stock_df.rename(columns={
        "Date": "trade_date",
        "Open": "open_price",
        "High": "high_price",
        "Low": "low_price",
        "Close": "close_price",
        "Adj Close": "adj_close_price",
        "Volume": "volume"
    })
    
    price_df = df[PRICE_COLUMNS].copy()

    # 필수 컬럼에 결측치가 있는 행 제거
    na_mask = price_df.isna().any(axis=1)
    if na_mask.any():
        logging.warning("%d rows removed due to missing values", na_mask.sum())
        price_df = price_df[~na_mask]

    # DB 스키마에 맞게 데이터 타입 변환
    price_df["trade_date"] = pd.to_datetime(price_df["trade_date"]).dt.date
    price_df["volume"] = price_df["volume"].astype("int64")   

    return price_df

def transform_daily_stock_indicator(price_df, last_dates):
    """
    주가 데이터를 기반으로 파생 지표를 계산하여 daily_stock_indicator 테이블 형식으로 변환한다. 

    Args:
        price_df (pd.DataFrame): 주가 정보 데이터프레임
        last_dates (dict[str, date]): 티커를 키로 마지막 수집 날짜를 갖는 딕셔너리

    Returns:
        pd.DataFrame: daily_stock_indicator 적재용 데이터프레임 (ticker, trade_date, 파생 지표)
    """

    if price_df.empty:
        return pd.DataFrame(columns=INDICATOR_COLUMNS)

    tickers = price_df["ticker"].unique().tolist()

    # 최초 적재와 증분 적재 대상을 분리
    backfill_tickers = [t for t in tickers if t not in last_dates]
    incremental_tickers = [t for t in tickers if t in last_dates]

    # 파생지표 계산을 위해 증분 적재 대상의 과거 데이터를 조회
    history_df = get_price_history_for_indicator(incremental_tickers, days=INDICATOR_LOOKBACK_DAYS)
    history_group = {
        t: df for t, df in history_df.groupby("ticker") 
    }

    indicator_rows = []

    for ticker in tickers:
        new_data = price_df[price_df["ticker"]==ticker][["trade_date", "adj_close_price", "volume"]].sort_values("trade_date")

        # 최초 데이터는 신규 데이터만 사용
        # 증분 적재는 과거 데이터와 합쳐 이동평균 계산
        if ticker in backfill_tickers:
            combined = new_data
        else:
            past_data = history_group.get(ticker, pd.DataFrame(columns=HISTORY_COLUMNS[1:]))
            combined = pd.concat([past_data, new_data], ignore_index=True).drop_duplicates("trade_date").sort_values("trade_date")

        combined["daily_return"] = combined["adj_close_price"].pct_change()
        combined["volume_change_rate"] = combined["volume"].pct_change()
        combined["ma5"] = combined["adj_close_price"].rolling(5).mean()
        combined["ma20"] = combined["adj_close_price"].rolling(20).mean()
        combined["ma60"] = combined["adj_close_price"].rolling(60).mean()
        combined["ma120"] = combined["adj_close_price"].rolling(120).mean()

        # 신규 데이터에 대해서만 계산 결과 저장
        result = combined[combined["trade_date"].isin(new_data["trade_date"])].copy()
        result["ticker"] = ticker

        indicator_rows.append(result) 

    indicator_df = pd.concat(indicator_rows, ignore_index=True)

    return indicator_df[INDICATOR_COLUMNS]