import logging
import os
from extract_stock import get_active_tickers, get_refresh_start_dates, extract_daily_stock_info
from transform_stock import transform_daily_stock_price, transform_daily_stock_indicator
from load_stock import load_stock_info
from etl_history import start_etl_job, finish_etl_job
from error_log import load_error_log
from config import REFRESH_LOOKBACK_DAYS

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "etl.log")
logging.basicConfig(
    filename=log_path, 
    filemode="a", 
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

def run_stock_etl():
    """
    주가 정보 ETL 파이프라인을 실행한다.

    ETL 작업 이력을 기록하고, 주가 정보를 추출 및 적재 한 뒤 
    작업 결과와 오류 정보를 데이터베이스에 저장한다.
    """

    job_id = None
    curr_step = "init"
    curr_task = "start_etl_job"

    try:
        job_id = start_etl_job("stock_etl")
        logger.info("Stock ETL started | job_id=%d", job_id)
        
        # Extract
        curr_step = "extract"
        curr_task = "get_active_tickers"
        tickers = get_active_tickers()
        logger.info("Retrieved %d active tickers", len(tickers))

        curr_task = "get_refresh_start_dates"
        refresh_start_dates = get_refresh_start_dates(tickers, days=REFRESH_LOOKBACK_DAYS)

        curr_task = "extract_daily_stock_info"
        stock_df, errors = extract_daily_stock_info(tickers, refresh_start_dates)
        logger.info("Extract completed: %d tickers, %d failed", stock_df["ticker"].nunique(), len(errors))

        # Transform
        curr_step = "transform"
        curr_task = "transform_daily_stock_price"
        price_df = transform_daily_stock_price(stock_df)

        curr_task = "transform_daily_stock_indicator"
        indicator_df = transform_daily_stock_indicator(price_df, refresh_start_dates)
        logger.info("Transform completed: %d price rows, %d indicator rows", len(price_df), len(indicator_df))

        # Load
        curr_step = "load"
        curr_task = "load_stock_info"
        load_stock_info(price_df, indicator_df)

        load_error_log(job_id, errors)
        logger.info("Load completed")

        status = "partial_success" if errors else "success"

        finish_etl_job(
            job_id,
            status,
            total_tickers=len(tickers),
            success_tickers=price_df["ticker"].nunique(),
            failed_tickers=len(errors)
        )
        logger.info("Stock ETL finished")

    except Exception as e:
        logger.exception("Stock ETL failed")

        if job_id is not None:
            try:
                # ETL 작업을 실패 상태로 종료한다.
                finish_etl_job(
                    job_id,
                    "failed",
                    total_tickers=None,
                    success_tickers=None,
                    failed_tickers=None
                )
            except Exception:
                logger.exception("Finish_etl_job failed")

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
                logger.exception("Load_error_log failed")
        raise

if __name__ == "__main__":
    run_stock_etl()