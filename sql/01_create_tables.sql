CREATE TABLE company (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    country VARCHAR(50),
    exchange VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE daily_stock_price (
    ticker VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price NUMERIC(12,4) NOT NULL CHECK (open_price >= 0),
    high_price NUMERIC(12,4) NOT NULL CHECK (high_price >= 0),
    low_price NUMERIC(12,4) NOT NULL CHECK (low_price >= 0),
    close_price NUMERIC(12,4) NOT NULL CHECK (close_price >= 0),
    adj_close_price NUMERIC(12,4) NOT NULL CHECK (adj_close_price >= 0),
    volume BIGINT NOT NULL CHECK (volume >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (ticker, trade_date),

    FOREIGN KEY (ticker)
        REFERENCES company(ticker),

    CHECK (high_price >= low_price),
    CHECK (open_price BETWEEN low_price AND high_price),
    CHECK (close_price BETWEEN low_price AND high_price)
);

CREATE TABLE daily_stock_indicator (
    ticker VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    daily_return NUMERIC(8,6),
    volume_change_rate NUMERIC(8,4),
    ma5 NUMERIC(12,4),
    ma20 NUMERIC(12,4),
    ma60 NUMERIC(12,4),
    ma120 NUMERIC(12,4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (ticker, trade_date), 

    FOREIGN KEY (ticker, trade_date)
        REFERENCES daily_stock_price(ticker, trade_date)
);

CREATE TABLE etl_job_history (
    job_id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    job_status VARCHAR(20) NOT NULL CHECK (job_status IN ('running', 'success', 'failed', 'partial_success')),
    total_record INT,
    success_record INT,
    failed_record INT,

    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE etl_error_log (
    error_id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL,
    ticker VARCHAR(10),
    pipeline_step VARCHAR(20) NOT NULL CHECK (pipeline_step in ('extract', 'transform', 'load')),
    task_name VARCHAR(100) NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_msg TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    FOREIGN KEY(job_id)
        REFERENCES etl_job_history(job_id)
);