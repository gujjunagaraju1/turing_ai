import logging
from playwright.sync_api import Page, expect
import re

from pages.login_page import LoginPage
from config.settings import SENDER_EMAIL, SENDER_PASSWORD, SENDER_USERNAME, NAV_TIMEOUT, RECEIVER_EMAIL

logger = logging.getLogger(__name__)


class TestLogin:

    # TC_LOGIN_001 — Valid login (username only)
    def test_valid_login(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login(SENDER_USERNAME, SENDER_PASSWORD)

        open_login_url.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        expect(open_login_url).to_have_url(re.compile(r"https://mail\.proton\.me/u/"))


    # TC_LOGIN_002 — Valid login (full email)
    def test_valid_login_with_full_email(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login(RECEIVER_EMAIL, SENDER_PASSWORD)
        open_login_url.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        expect(open_login_url).to_have_url(re.compile(r"https://mail\.proton\.me/u/"))


    # TC_LOGIN_003 — Wrong password → error shown
    def test_invalid_password(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login(SENDER_USERNAME, "WrongPassword@999")
        open_login_url.wait_for_timeout(3000)
        assert login.check_error_message()
        assert "The password is not correct" in login.get_error_message()

    # TC_LOGIN_004 — invalid credentials
    def test_empty_username(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login("hhsjjsj", "WrongPassword@999")

        open_login_url.wait_for_timeout(3000)
        assert login.check_error_message()
