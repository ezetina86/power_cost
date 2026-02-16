## 2024-05-22 - [Optimizing Pandas Date Parsing]
**Learning:** `pd.read_csv(parse_dates=['Col'])` can be significantly slower (~1.5x) than `pd.to_datetime(df['Col'])` for standard ISO8601 strings in some environments. Also, explicit `df.copy()` in transformation functions is a major performance killer for large DataFrames.
**Action:** Prefer `pd.to_datetime` over `read_csv` parsing for simple formats unless proven otherwise. Always audit data pipelines for unnecessary copies.
