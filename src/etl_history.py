from sqlalchemy import text
from db import engine

def start_etl_job(job_name):
    """
    ETL 작업 시작 이력을 etl_job_history 테이블에 저장한다.

    Args:
        job_name (str): 실행 중인 ETL 작업의 이름.

    Returns:
        int: 새로 생성된 ETL 작업 이력의 고유 식별자(job_id).
    """

    query = text("""
        INSERT INTO etl_job_history (job_name, job_status)
        VALUES (:job_name, :job_status)
        RETURNING job_id;
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"job_name": job_name, "job_status": "running"})
        job_id = result.scalar_one()

    return job_id
    
def finish_etl_job(job_id, job_status, total_tickers, success_tickers, failed_tickers):
    """
    ETL 작업 종료 정보를 etl_job_history 테이블에 업데이트 한다.

    Args:
        job_id (int): ETL 작업 이력의 고유 식별자.
        job_status (str): ETL 작업의 최종 상태 (예: success, failed).
        total_tickers (int): 처리한 전체 티커 수.
        success_tickers (int): 처리에 성공한 티커 수.
        failed_tickers (int): 처리에 실패한 티커 수.
    """

    query = text("""
        UPDATE etl_job_history
        SET 
            ended_at = NOW(),
            job_status = :job_status,
            total_tickers = :total_tickers,
            success_tickers = :success_tickers,
            failed_tickers = :failed_tickers
        WHERE job_id = :job_id;
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "job_id": job_id, 
            "job_status": job_status,
            "total_tickers": total_tickers,
            "success_tickers": success_tickers,
            "failed_tickers": failed_tickers
            })