"""
Pytest configuration for tinygenkey test suite.

Provides test markers and basic configuration.
"""

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "security: security-focused tests"
    )
    config.addinivalue_line(
        "markers", "performance: performance benchmark tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: edge case and boundary tests"
    )
