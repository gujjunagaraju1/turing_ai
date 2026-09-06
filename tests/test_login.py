import logging
import re
import allure
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from config.settings import SENDER_EMAIL, SENDER_PASSWORD, SENDER_USERNAME, NAV_TIMEOUT, RECEIVER_EMAIL

logger = logging.getLogger(__name__)


@allure.feature("Authentication")
@allure.epic("Proton Mail Core")
@pytest.mark.auth
class TestLogin:

    # TC_LOGIN_001 — Valid login (username only)
    @allure.story("User Login")
    @allure.title("TC-LOGIN-01: Valid login with username only")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    @pytest.mark.regression
    @pytest.mark.smoke
    def test_valid_login(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login(SENDER_USERNAME, SENDER_PASSWORD)

        open_login_url.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        expect(open_login_url).to_have_url(re.compile(r"https://mail\.proton\.me/u/"))

    # TC_LOGIN_002 — Valid login and logout
    @allure.story("User Session")
    @allure.title("TC-LOGIN-02: Valid login and clean logout")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    @pytest.mark.regression
    def test_valid_login_and_logout(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login(SENDER_USERNAME, SENDER_PASSWORD)

        open_login_url.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        expect(open_login_url).to_have_url(re.compile(r"https://mail\.proton\.me/u/"))
        login.logout_user()
           
    # TC_LOGIN_003 — Valid login (full email)
    @allure.story("User Login")
    @allure.title("TC-LOGIN-03: Valid login with full email address")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_valid_login_with_full_email(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login(RECEIVER_EMAIL, SENDER_PASSWORD)
        open_login_url.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        expect(open_login_url).to_have_url(re.compile(r"https://mail\.proton\.me/u/"))

    # TC_LOGIN_004 — Wrong password → error shown
    @allure.story("Negative Authentication")
    @allure.title("TC-LOGIN-04: Login attempt with incorrect password")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.negative
    def test_invalid_password(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login(SENDER_USERNAME, "WrongPassword@999")
        open_login_url.wait_for_timeout(3000)
        assert login.check_error_message()
        assert "The password is not correct" in login.get_error_message()

    # TC_LOGIN_005 — invalid credentials
    @allure.story("Negative Authentication")
    @allure.title("TC-LOGIN-05: Login attempt with unregistered username")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.negative
    def test_empty_username(self, open_login_url):
        login = LoginPage(open_login_url)
        login.login("hhsjjsj", "WrongPassword@999")

        open_login_url.wait_for_timeout(3000)
        assert login.check_error_message()
