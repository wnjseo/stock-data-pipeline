import logging
import os
from extract_company import get_company_list, extract_company_info
from load_company import load_company_info
from etl_history import start_etl_job, finish_etl_job
from error_log import load_error_log

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "etl.log")
logging.basicConfig(
    filename=log_path, 
    filemode="a", 
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def run_company_etl():
    """
    회사 정보 ETL 파이프라인을 실행한다.

    ETL 작업 이력을 기록하고, 회사 정보를 추출 및 적재 한 뒤 
    작업 결과와 오류 정보를 데이터베이스에 저장한다.
    """

    job_id = None
    curr_step = "init"
    curr_task = "start_etl_job"

    try:
        job_id = start_etl_job("company_etl")
        logger.info("company ETL started | job_id=%d", job_id)
        
        # Extract
        curr_step = "extract"
        curr_task = "get_company_list"
        tickers = get_company_list()
        logger.info("Scraped %d tickers", len(tickers))

        curr_task = "extract_company_info"
        company_df, errors = extract_company_info(tickers)
        logger.info("Extract completed: %d tickers, %d failed", len(company_df), len(errors))

        # Load
        curr_step = "load"
        curr_task = "load_company_info"
        load_company_info(company_df, tickers)

        load_error_log(job_id, errors)
        logger.info("Load completed")

        status = "partial_success" if errors else "success"

        finish_etl_job(
            job_id,
            status,
            total_record=len(tickers),
            success_record=len(company_df),
            failed_record=len(errors)
        )
        logger.info("company ETL finished")

    except Exception as e:
        if job_id is not None:
            try:
                # ETL 작업을 실패 상태로 종료한다.
                finish_etl_job(
                    job_id,
                    "failed",
                    total_record=None,
                    success_record=None,
                    failed_record=None
                )
            except Exception:
                logger.exception("finish_etl_job failed")

            try:
                # 파이프라인 자체에서 발생한 오류를 기록한다.
                errors = [{
                    "ticker": None,
                    "pipeline_step": curr_step,
                    "task_name": curr_task,
                    "error_type": type(e).__name__,
                    "error_msg": str(e)
                }]

                load_error_log(job_id, errors)
            except Exception:
                logger.exception("load_error_log failed")
        raise

if __name__ == "__main__":
    run_company_etl()