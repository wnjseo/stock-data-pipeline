from sqlalchemy import text, bindparam
from db import engine

def load_company_info(company_df, tickers):
    """
    회사 정보 데이터프레임을 company 테이블에 저장한다.
    
    기존 ticker가 존재하면 UPDATE, 존재하지 않으면 INSERT 한다.
    
    Args: 
        company_df (pd.DataFrame): 회사 정보 데이터프레임
        tickers (list): 이번 실행에서 조회를 시도한 전체 티커 목록
    """

    # 저장할 데이터가 없으면 DB 작업을 수행하지 않는다.
    if company_df.empty or not tickers:
        return
    
    records = company_df.to_dict("records")

    upsert_query = text("""
        INSERT INTO company (ticker, company_name, sector, industry, country, exchange, is_active)
        VALUES (:ticker, :company_name, :sector, :industry, :country, :exchange, TRUE)
        -- ticker를 기준으로 중복 시 최신 정보로 갱신 
        ON CONFLICT (ticker)
        DO UPDATE SET
            company_name = EXCLUDED.company_name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry,
            country = EXCLUDED.country,
            exchange = EXCLUDED.exchange,
            is_active = TRUE;
    """)

    deactivate_query = text("""
        UPDATE company 
        SET is_active = FALSE
        WHERE is_active = TRUE AND ticker NOT IN :tickers;
    """).bindparams(bindparam("tickers", expanding=True))

    with engine.begin() as conn:
        conn.execute(upsert_query, records)
        conn.execute(deactivate_query, {"tickers": tickers})