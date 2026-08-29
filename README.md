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

## Backfill / Incremental 전략

## Data Quality

## Error Handling

## Retry

## 실행 방법

## 발견한 실제 문제와 해결 방법

## 한계 및 향후 개선 사항