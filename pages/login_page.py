# ═══════════════════════════════════════════════════════════════
# pages/login_page.py — Login Page (Locators + Actions)
# ═══════════════════════════════════════════════════════════════

import logging
from playwright.sync_api import Page
from config.settings import  NAV_TIMEOUT, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class LoginPage:

    # ── LOCATORS ─────────────────────────────────────────────────
    LOC_USERNAME_INPUT = "//input[@id='username']"
    LOC_PASSWORD_INPUT = "//input[@id='password']"
    LOC_SIGN_IN_BUTTON = "//button[@type='submit']"
    LOC_ERROR_MESSAGE="//div[@data-testid='login:error-block']"

    # ── CONSTRUCTOR ──────────────────────────────────────────────
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator(self.LOC_USERNAME_INPUT)
        self.password_input = page.locator(self.LOC_PASSWORD_INPUT)
        self.sign_in_button = page.locator(self.LOC_SIGN_IN_BUTTON)
        self.error_message=page.locator(self.LOC_ERROR_MESSAGE)

    # ── ACTIONS ──────────────────────────────────────────────────
    def navigate(self):
        """Navigate directly to the login page."""
        self.page.goto("https://account.proton.me", timeout=NAV_TIMEOUT)
        self.page.wait_for_load_state("domcontentloaded")

    def enter_username(self, username: str):
        self.username_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.username_input.clear()
        self.username_input.fill(username)

    def enter_password(self, password: str):
        self.password_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.password_input.clear()
        self.password_input.fill(password)

    def click_sign_in(self):
        self.sign_in_button.click()

    def login(self, username: str, password: str):
        self.enter_username(username)
        self.enter_password(password)
        self.click_sign_in()


    def check_error_message(self)->bool:
        return self.error_message.is_visible()

    def get_error_message(self)->str:
        return self.error_message.inner_text()
