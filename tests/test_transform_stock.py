import pytest
import pandas as pd
import numpy as np
import datetime
from transform_stock import transform_daily_stock_price, transform_daily_stock_indicator
from config import PRICE_COLUMNS

@pytest.fixture
def mock_raw_df():
    return pd.DataFrame({
        "ticker": ["TEST", "TEST"],
        "Date": ["2026-08-12", "2026-08-13"],
        "Open": [200.0, 201.0],
        "High": [205.0, 206.0],
        "Low": [198.0, 199.0],
        "Close": [203.0, 204.0],
        "Adj Close": [203.0, 204.0],
        "Volume": [1000, 1100]
    })

def test_transform_success(mock_raw_df):
    """
    정상적인 OHLCV는 ohlc_valid=True로 표시되어야 한다. 
    """
    result = transform_daily_stock_price(mock_raw_df)

    assert result.iloc[0]["ohlc_valid"]

def test_transform_empty_df():
    """
    빈 입력은 PRICE_COLUMNS를 가진 빈 데이터프레임을 반환해야 한다.
    """
    result = transform_daily_stock_price(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == PRICE_COLUMNS

def test_transform_missing_value(mock_raw_df):
    """
    필수 컬럼에 결측치가 있는 행은 제거되어야 한다.
    """
    df = mock_raw_df.copy()
    df.loc[0, "Volume"] = np.nan

    result = transform_daily_stock_price(df)

    assert len(result) == 1
    assert result.iloc[0]["trade_date"] == datetime.date(2026, 8, 13)

def test_transform_open_below_low(mock_raw_df):
    """
    open이 low보다 낮으면 ohlc_valid=False로 표시되어야 하고,
    값 자체는 원본 그대로 보존되어야 한다.
    """
    df = mock_raw_df.copy()
    df.loc[0, "Open"] = 195

    result = transform_daily_stock_price(df)

    assert not result.iloc[0]["ohlc_valid"]
    assert result.iloc[0]["open_price"] == 195

def test_transform_close_above_high(mock_raw_df):
    """
    close가 high보다 높으면 ohlc_valid=False로 표시되어야 하고,
    값 자체는 원본 그대로 보존되어야 한다.
    """
    df = mock_raw_df.copy()
    df.loc[0, "Close"] = 210

    result = transform_daily_stock_price(df)

    assert not result.iloc[0]["ohlc_valid"]
    assert result.iloc[0]["close_price"] == 210

def test_transform_data_type(mock_raw_df):
    """
    DB 스키마에 맞게 데이터 타입이 변환되어야 한다.
    """
    result = transform_daily_stock_price(mock_raw_df)

    assert isinstance(result.iloc[0]["trade_date"], datetime.date)
    assert result["volume"].dtype == "int64"