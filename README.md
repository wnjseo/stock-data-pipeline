# 📈 Stock-Data-Pipeline

S&P 500 구성 종목의 일별 주가 데이터를 자동 수집하여 PostgreSQL에 적재하는 ETL 파이프라인입니다.

## 🎯 프로젝트 목적
- S&P 500 구성 종목의 일별 주가 데이터를 자동으로 수집하고 PostgreSQL에 적재하는 데이터 파이프라인입니다. 
단순 데이터 수집을 넘어 안정적인 ETL 운영을 목표로 Backfill 및 Incremental Load, 데이터 품질 검증, 재시도, 오류 로깅 등의 ETL 기능을 구현하는 것을 목표로 합니다.

## 🛠️ Tech Stack

### Data Pipeline & Logic
- **Python**
- **yfinance**
- **Pandas**

### Database & ORM
- **PostgreSQL**
- **SQLAlchemy**
- **psycopg2**

### Testing & Operations
- **Git / Github**
- **pytest**
- **dotenv**
- **Window Task Scheduler**

## Architecture
```mermaid
flowchart TD
    W[Windows Task Scheduler] --> |Weekly / Monthly| E1[Extract]
    W --> |After Market Close| E2[Load Active Symbols]
    subgraph CompanyETL["Company ETL"]
        Wiki[Wikipedia / S&P 500 List] --> |Ticker 수집| E1
        E1 --> L1[Load]
        L1 --> |Upsert| DB1[(Company Table)]
    end
    subgraph StockETL["Stock ETL"]
        DB1 --> |S&P 500 active symbols| E2
        E2 --> C{최근 적재일 <br/> 존재?}
        C --> |No| B[Backfill]
        C --> |Yes| I[Incremental]
        B --> Y[yfinance]
        I --> Y
        Y --> T[Transform]
        T --> L2[Load] 
        L2 --> |Upsert| DB2[(Stock Table)]
    end
    CompanyETL -.오류시.-> E[(etl_error_log)]
    StockETL -.오류시.-> E
    CompanyETL -.실행기록.-> J[(etl_job_history)]
    StockETL -.실행기록.-> J
    J ~~~ E

    style CompanyETL fill:#fff7e6
    style StockETL fill:#e6f0ff
```

## Data Flow
```mermaid
flowchart LR
```

## DB Schema
```mermaid
erDiagram
    company ||--o{ daily_stock_price : has
    daily_stock_price ||--o| daily_stock_indicator : has
    etl_job_history ||--o{ etl_error_log : has
    company {
        VARCHAR ticker PK
        VARCHAR company_name
        VARCHAR sector
        VARCHAR industry
        VARCHAR country
        VARCHAR exchange
        BOOLEAN is_active
    }
    daily_stock_price {
        VARCHAR ticker PK,FK
        DATE trade_date PK
        NUMERIC open_price
        NUMERIC high_price
        NUMERIC low_price
        NUMERIC close_price
        NUMERIC adj_close_price
        BIGINT volume
        BOOLEAN ohlc_valid
        TIMESTAMPTZ created_at
    }
    daily_stock_indicator {
        VARCHAR ticker PK,FK
        DATE trade_date PK,FK
        NUMERIC daily_return 
        NUMERIC volume_change_rate 
        NUMERIC ma5 
        NUMERIC ma20 
        NUMERIC ma60 
        NUMERIC ma120
        TIMESTAMPTZ created_at
    }
    etl_job_history {
        BIGSERIAL job_id PK
        VARCHAR job_name
        TIMESTAMPTZ started_at
        TIMESTAMPTZ ended_at
        VARCHAR job_status
        INT total_tickers 
        INT success_tickers
        INT failed_tickers
    }
    etl_error_log {
        BIGSERIAL error_id PK
        BIGINT job_id FK
        VARCHAR ticker
        VARCHAR pipeline_step
        VARCHAR task_name
        VARCHAR error_type
        TEXT error_msg
        TIMESTAMPTZ occurred_at
    }
```

- **is_active**: 현재 S&P 500 구성 종목과 과거 구성 종목을 구분하며, 구성에서 제외된 종목의 과거 데이터는 삭제하지 않는다.
- **ohlc_valid**: yfinance가 반환하는 원천 데이터의 OHLC 이상 여부를 기록하여, 이상 데이터를 삭제하지 않고 추적할 수 있도록 한다.
- **(ticker, trade_date) 복합 PK**: 종목별 거래일을 유일하게 식별하여 동일 종목의 동일 거래일 데이터 중복 적재를 방지한다.

## Backfill / Incremental 전략

## Data Quality

### 검증 항목
- **OHLC 관계 검증**: `high >= low`, `high >= open/close`, `low <= open/close` 조건을 검증한다. 조건을 만족하지 않는 데이터는 삭제하지 않고 `ohlc_valid = False`로 표시하여 원천 데이터의 이상 여부를 추적할 수 있도록 한다.
- **값의 범위 검증**: 가격과 거래량이 음수가 되지 않도록 DB CHECK 제약조건을 적용하여 비정상적인 값의 적재를 방지한다.
- **중복 데이터 방지**: `(ticker, trade_date)`를 복합 PK로 설정하여 동일 종목의 동일 거래일 데이터가 중복 저장되지 않도록 한다.

### 설계 원칙
- **원천 데이터 보존**: yfinance가 반환하는 값 자체가 잘못되는 경우가 있어 이상 데이터를 임의로 삭제하지 않고 검증 결과를 별도의 컬럼으로 기록한다.
- **Python + DB 이중 검증**: Python 변환 과정에서 데이터 유효성을 확인하고, DB 제약조건을 통해 최종 적재 단계에서도 데이터 무결성을 보장한다.
- **추적 가능성**: 데이터의 이상 여부를 별도로 기록하여 이후 원천 데이터 문제와 변환 로직 문제를 구분할 수 있도록 한다.

## Error Handling

### 기록 구조
- **ticker, task_name**: 오류가 발생한 종목과 작업을 식별한다. 종목과 무관한 전체 오류의 경우 `ticker`는 `NULL`로 기록한다.
- **pipeline_step**: `extract/transform/load` 중 어느 단계에서 오류가 발생했는지 기록하여 장애 원인을 빠르게 좁힐 수 있도록 한다.
- **error_type, error_msg**: 오류 유형과 상세 메세지를 남겨 재현 및 원인 분석에 활용한다.

### 설계 의도
`etl_job_history`는 ETL 실행 단위의 처리 결과를 요약하고, `etl_error_log`는 해당 실행 중 발생한 개별 오류의 상세 정보를 기록하도록 한다.
개별 종목의 실패가 전체 ETL 실행 실패로 이어지지 않도록 오류를 수집하고 다른 종목의 처리를 계속한다. 전체 작업은 성공한 종목과 실패한 종목의 결과에 따라 `success`, `partial_success`, `failed` 상태로 종료할 수 있도록 한다.
ETL 실행 중 발생한 오류는 `errors`에 수집한 후, 전체 ETL 실행이 완료되면 `etl_error_log`에 일괄 적재한다.

## Retry

### 재시도 대상
종목 단위(ticker)로 `yfinance API` 호출을 재시도 한다. 네트워크 타임아웃, rate limit(HTTP 429), 빈 데이터 반환 등의 일시적으로 발생할 수 있는 오류를 재시도 대상으로 한다.

### 재시도 정책
- **MAX_RETRIES = 3**: 동일 종목에 대해 최대 3회까지 시도한다.
- **RETRY_DELAY = 1**: 재시도 사이에 1초의 대기시간을 둔다.
- **최종 실패 처리**: 3회 모두 실패한 종목은 `errors`로 집계하고 해당 종목의 처리를 종료한다. 다른 종목의 처리는 계속하여 도중에 전체 ETL이 중단되지 않도록 한다.

## 실행 방법

### Installation
```bash
git clone https://github.com/wnjseo/stock-data-pipeline
cd stock-data-pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
1. `env`파일을 열어 DB 접속 정보를 입력
```bash
copy .env.example .env
```

```bash
DB_HOST = localhost
DB_PORT = 5432
DB_NAME = stock_etl
DB_USER = your_user
DB_PW = your_pw
```
2. 스키마 생성
```bash
   psql -U your_user -d stock_etl -f 01_create_tables.sql
```

### Run
```bash
# 회사 정보 ETL (주 1회 실행 권장)
python main_company.py
# 주가 ETL (장 마감 후 실행 권장)
python main_stock.py
```

## 발견한 실제 문제와 해결 방법

## 한계 및 향후 개선 사항