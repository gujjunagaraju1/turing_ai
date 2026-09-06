# ═══════════════════════════════════════════════════════════════
# tests/conftest.py — Shared fixtures for all tests in /tests
# ═══════════════════════════════════════════════════════════════
#
# FIXTURE GUIDE — use the right fixture in each test:
#
#   open_login_url  → for LOGIN tests (navigates to login page only)
#                     Usage: def test_foo(self, open_login_url)
#
#   logged_in_page  → for COMPOSE / post-login tests (navigates + logs in)
#                     Usage: def test_foo(self, logged_in_page)
#
# NOTE: No autouse here — nothing runs automatically.
#       Each test requests only what it needs → no double navigation.
# ───────────────────────────────────────────────────────────────

import pytest

from config.settings import (
    NAV_TIMEOUT,
    BASE_URL,
    SENDER_PASSWORD,
    SENDER_USERNAME,
)
from pages.login_page import LoginPage


# ── For: test_login.py ───────────────────────────────────────────
# Navigates to the login page and returns the raw page.
# Login tests then perform login themselves.
@pytest.fixture
def open_login_url(page):
    page.goto(BASE_URL, timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded")
    return page



@pytest.fixture
def logged_in_page(page):
    page.goto(BASE_URL, timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded")

    login = LoginPage(page)
    login.login(SENDER_USERNAME, SENDER_PASSWORD)

    page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)

    return page
