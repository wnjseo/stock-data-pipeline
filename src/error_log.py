from sqlalchemy import text
from db import engine

def load_error_log(job_id, errors):
    """
    오류 발생 정보를 etl_error_log 테이블에 저장한다.

    Args:
        job_id (int): ETL 작업 이력의 고유 식별자. 
        errors (list[dict]): 오류 정보를 담은 딕셔너리 리스트.
            각 딕셔너리는 ticker, pipeline_step, task_name, error_type, error_msg를 포함한다.
    """

    # 저장할 오류가 없으면 DB 작업을 수행하지 않는다.
    if not errors:
        return
    
    query = text("""
        INSERT INTO etl_error_log (job_id, ticker, pipeline_step, task_name, error_type, error_msg)
        VALUES (:job_id, :ticker, :pipeline_step, :task_name, :error_type, :error_msg)
    """)

    records = [
        {"job_id":job_id, **error}
        for error in errors
    ]

    with engine.begin() as conn:
        conn.execute(query, records)