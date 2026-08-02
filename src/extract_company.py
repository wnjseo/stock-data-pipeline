import time
import yfinance as yf
import pandas as pd
import requests
from config import MAX_RETRIES, RETRY_DELAY, REQUEST_DELAY, COMPANY_COLUMNS

def get_company_list():
    """ 
    위키피디아의 S&P 500 기업 목록에서 티커(Symbol)을 조회한다. 
    
    Returns:
        list[str]: 조회한 S&P 500 티커 목록
    """

    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    
    table = pd.read_html(response.text)

    # BRK.B와 같은 티커를 yfinance 형식(BRK-B)으로 변환
    tickers = table[0]["Symbol"].str.replace(".", "-", regex=False).tolist()
    
    return tickers
    
def extract_company_info(tickers):
    """ 
    yfinance에서 S&P 500 기업 정보를 조회한다. 
    
    Args:
        tickers (list): 조회한 S&P 500 티커 목록 

    Returns:
        tuple[pd.DataFrame, list[dict]]:
            - 회사 정보 데이터프레임
            - 조회에 실패한 티커의 오류 정보 목록
    """

    companies = []
    errors = []
    
    for ticker in tickers:
        # 티커 하나당 3번까지 재시도
        for attempt in range(MAX_RETRIES):
            try:
                info = yf.Ticker(ticker).info

                companies.append({
                    "ticker": ticker,
                    # longName이 없으면 shortName, 둘 다 없으면 ticker를 사용
                    "company_name": info.get("longName") or info.get("shortName") or ticker,
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "country": info.get("country"),
                    "exchange": info.get("exchange")
                })
                break

            except Exception as e:
                if attempt == MAX_RETRIES-1:
                    errors.append({
                        "ticker": ticker,
                        "pipeline_step": "extract",
                        "task_name": "extract_company_info",
                        "error_type": type(e).__name__,
                        "error_msg": str(e)
                    })
                else:
                    time.sleep(RETRY_DELAY)
        # API 호출 간격을 두어 과도한 요청을 방지한다.
        time.sleep(REQUEST_DELAY)

    if not companies:
        return pd.DataFrame(columns=COMPANY_COLUMNS), errors

    return pd.DataFrame(companies, columns=COMPANY_COLUMNS), errors