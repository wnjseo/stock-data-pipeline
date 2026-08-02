from sqlalchemy import text
import pandas as pd
from db import engine

def load_stock_info(price_df, indicator_df):
    """
    변환한 주가 정보 데이터와 파생 지표 데이터를 각각 
    daily_stock_price, daily_stock_indicator 테이블에 저장한다.

    Args:
        price_df (pd.DataFrame): daily_stock_price 적재용 데이터프레임
        indicator_df (pd.DataFrame): daily_stock_indicator 적재용 데이터프레임
    """

    if price_df.empty or indicator_df.empty:
        return
    
    # NaN을 SQL NULL로 변환
    price_records = [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in price_df.to_dict("records")
    ]
    indicator_records = [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in indicator_df.to_dict("records")
    ]

    price_query = text("""
        INSERT INTO daily_stock_price (ticker, trade_date, open_price, high_price, low_price, close_price, adj_close_price, volume)
        VALUES (:ticker, :trade_date, :open_price, :high_price, :low_price, :close_price, :adj_close_price, :volume)
        ON CONFLICT (ticker, trade_date) DO UPDATE SET
            open_price = EXCLUDED.open_price,
            high_price = EXCLUDED.high_price,
            low_price = EXCLUDED.low_price,
            close_price = EXCLUDED.close_price,
            adj_close_price = EXCLUDED.adj_close_price,
            volume = EXCLUDED.volume;
    """)

    indicator_query = text ("""
        INSERT INTO daily_stock_indicator (ticker, trade_date, daily_return, volume_change_rate, ma5, ma20, ma60, ma120)
        VALUES (:ticker, :trade_date, :daily_return, :volume_change_rate, :ma5, :ma20, :ma60, :ma120)
        ON CONFLICT (ticker, trade_date) DO UPDATE SET
            daily_return = EXCLUDED.daily_return,
            volume_change_rate = EXCLUDED.volume_change_rate,
            ma5 = EXCLUDED.ma5,
            ma20 = EXCLUDED.ma20,
            ma60 = EXCLUDED.ma60,
            ma120 = EXCLUDED.ma120;
    """)

    with engine.begin() as conn:
        conn.execute(price_query, price_records)
        conn.execute(indicator_query, indicator_records)