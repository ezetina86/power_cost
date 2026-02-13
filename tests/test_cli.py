"""Tests for power_cost.cli module."""

import logging

from power_cost.cli import main


class TestCLIMain:
    """Tests for the CLI main function."""

    def test_main_logs_message(self, caplog):
        """Verify main() logs a 'not yet implemented' message."""
        with caplog.at_level(logging.INFO):
            main()
        assert any("not yet implemented" in r.message for r in caplog.records)

    def test_main_returns_none(self):
        """Verify main() returns None."""
        result = main()
        assert result is None
