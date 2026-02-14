## 2025-05-24 - [Testing Cached Functions]
**Learning:** When testing a function that wraps another function with `@st.cache_data`, simply patching the inner function may not be enough for unit tests of the caller. The `st.cache_data` decorator adds logic that might interfere or swallow mocks if not properly initialized.
**Action:** When unit testing logic that calls a cached wrapper (e.g., `main` calling `get_data`), mock the wrapper function (`get_data`) directly instead of the inner function (`load_power_log`) to isolate the caller's logic from the caching mechanism.
