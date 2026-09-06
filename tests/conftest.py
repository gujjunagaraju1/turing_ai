# ═══════════════════════════════════════════════════════════════
# tests/conftest.py — Auto-setup for all tests in this folder
# ═══════════════════════════════════════════════════════════════
#
# autouse=True → runs automatically before EVERY test here
# No need to call login.navigate() inside each test anymore
# ───────────────────────────────────────────────────────────────

import pytest
from config.settings import NAV_TIMEOUT,BASE_URL


@pytest.fixture(autouse=True)
def open_login_url(page):
    page.goto(BASE_URL, timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded")
