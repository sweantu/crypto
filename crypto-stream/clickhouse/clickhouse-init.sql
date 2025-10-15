CREATE DATABASE IF NOT EXISTS testdb;

CREATE TABLE IF NOT EXISTS klines (
    window_start DateTime(3),
    window_end DateTime(3),
    open_price Float64,
    high_price Float64,
    low_price Float64,
    close_price Float64,
    volume Float64,
    symbol String
) ENGINE = MergeTree()
ORDER BY (symbol, window_start);

CREATE TABLE IF NOT EXISTS engulfings (
    window_start DateTime(3),
    window_end DateTime(3),
    open_price Float64,
    high_price Float64,
    low_price Float64,
    close_price Float64,
    volume Float64,
    ema7 Float64,
    ema20 Float64,
    trend String,
    engulfing_pattern String,
    symbol String
) ENGINE = MergeTree()
ORDER BY (symbol, window_start);