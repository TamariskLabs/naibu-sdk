"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

BASE_URL = "https://api.test.naibu.com"


@pytest.fixture
def base_url() -> str:
    return BASE_URL
