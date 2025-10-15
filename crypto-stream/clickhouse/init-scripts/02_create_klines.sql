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