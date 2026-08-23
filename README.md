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
    %% 노드 정의
    Wiki[Wikipedia / S&P 500 List] -->|1. Ticker 수집| Extractor[Python Data Extractor]
    YF[yfinance API] <-->|2. 주가 데이터 요청/응답| Extractor
    
    Extractor -->|3. 원시 데이터 저장| Raw[Raw Data / Local Parquet]
    Raw -->|4. 정제 및 포맷팅| Transformer[Pandas Transformer]
    
    Transformer -->|5. DB Insert/Upsert| DB[(PostgreSQL)]
    
    Scheduler[Cron / Airflow] -->|매일 장 마감 후 실행| Extractor
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