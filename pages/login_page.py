import logging
from playwright.sync_api import Page
from config.settings import NAV_TIMEOUT, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class LoginPage:
    LOC_USERNAME_INPUT = "//input[@id='username']"
    LOC_PASSWORD_INPUT = "//input[@id='password']"
    LOC_SIGN_IN_BUTTON = "//button[@type='submit']"
    LOC_ERROR_MESSAGE = "//div[@data-testid='login:error-block']"
    LOC_CLICK_ON_USER = "//button[@data-testid='heading:userdropdown']"
    LOC_CLICK_ON_LOGOUT = "//button[@data-testid='userdropdown:button:logout']"

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator(self.LOC_USERNAME_INPUT)
        self.password_input = page.locator(self.LOC_PASSWORD_INPUT)
        self.sign_in_button = page.locator(self.LOC_SIGN_IN_BUTTON)
        self.error_message = page.locator(self.LOC_ERROR_MESSAGE)
        self.click_on_user = page.locator(self.LOC_CLICK_ON_USER)
        self.click_on_logout = page.locator(self.LOC_CLICK_ON_LOGOUT)

    def navigate(self):
        self.page.goto("https://account.proton.me", timeout=NAV_TIMEOUT)
        self.page.wait_for_load_state("domcontentloaded")

    def enter_username(self, username: str):
        self.username_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.username_input.click()
        self.username_input.fill(username)

    def enter_password(self, password: str):
        self.password_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.password_input.click()
        self.password_input.fill(password)

    def click_sign_in(self):
        self.sign_in_button.click()

    def login(self, username: str, password: str):
        self.enter_username(username)
        self.enter_password(password)
        self.click_sign_in()

    def check_error_message(self) -> bool:
        return self.error_message.is_visible()

    def get_error_message(self) -> str:
        return self.error_message.inner_text()

    def logout_user(self):
        self.click_on_user.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.click_on_user.click()
        self.click_on_logout.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.click_on_logout.click()
        self.page.wait_for_load_state("domcontentloaded")
        self.username_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        logger.info("User logged out successfully and returned to login screen")
