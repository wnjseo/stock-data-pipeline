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
    subgraph Company ETL
        Wiki[Wikipedia / S&P 500 List] --> |Ticker 수집| E1[Extract]
        E1 --> L1[Load]
        L1 --> |Upsert| DB1[(Company Table)]
    end
    subgraph Stock ETL
        Extract2 --> Transform[Transform]
        Transform --> Load2[Load] 
        Load2 --> |Upsert| DB2[[(Stock Table)]]
    end
```

## Data Flow

## DB Schema

## Backfill / Incremental 전략

## Data Quality

## Error Handling

## Retry

## 실행 방법

## 발견한 실제 문제와 해결 방법

## 한계 및 향후 개선 사항