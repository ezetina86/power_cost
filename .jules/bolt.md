## 2025-02-13 - [Pandas NaN filtering Optimization]
**Learning:** Chained pandas operations like `dropna()` followed by boolean filtering are significantly slower (3x in this case) than a single boolean mask because each step creates a new DataFrame/copy. Also, `NaN >= 0` is False, so explicit `dropna` is often redundant for threshold checks.
**Action:** Combine validation checks into a single mask where possible, and leverage implicit NaN handling in comparisons.
