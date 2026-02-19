## 2024-05-22 - [Optimizing Pandas Date Parsing]
**Learning:** `pd.read_csv(parse_dates=['Col'])` can be significantly slower (~1.5x) than `pd.to_datetime(df['Col'])` for standard ISO8601 strings in some environments. Also, explicit `df.copy()` in transformation functions is a major performance killer for large DataFrames.
**Action:** Prefer `pd.to_datetime` over `read_csv` parsing for simple formats unless proven otherwise. Always audit data pipelines for unnecessary copies.

## 2025-02-13 - [Pandas NaN filtering Optimization]
**Learning:** Chained pandas operations like `dropna()` followed by boolean filtering are significantly slower (3x in this case) than a single boolean mask because each step creates a new DataFrame/copy. Also, `NaN >= 0` is False, so explicit `dropna` is often redundant for threshold checks.
**Action:** Combine validation checks into a single mask where possible, and leverage implicit NaN handling in comparisons.

## 2026-02-18 - [Optimizing CSV Loading with Usecols]
**Learning:** `pd.read_csv(usecols=[...])` significantly improves performance by only reading necessary columns and implicitly validates their existence, raising a standard `ValueError` if missing. This avoids reading extra data and the need for a separate validation step, but changes the error message.
**Action:** Use `usecols` in `read_csv` when possible to optimize I/O and memory, and update tests to expect standard pandas error messages.
