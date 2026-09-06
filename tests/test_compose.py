import logging
import re
import allure
import pytest
from playwright.sync_api import Page, expect

from pages.compose_page import ComposePage
from config.settings import SENDER_EMAIL, SENDER_PASSWORD, SENDER_USERNAME, NAV_TIMEOUT, RECEIVER_EMAIL

logger = logging.getLogger(__name__)


@allure.feature("Email Composition")
@allure.epic("Proton Mail Core")
@pytest.mark.compose
class TestCompose:
    
    # ─────────────────────────────────────────────────────────────
    # TC-01 [POSITIVE] — Send email with all fields filled
    # Expected: Email is sent successfully (composer closes)
    # ─────────────────────────────────────────────────────────────
    @allure.story("Compose and Send")
    @allure.title("TC-COMP-01: Send email with all fields filled")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    @pytest.mark.regression
    @pytest.mark.smoke
    def test_send_email_with_all_fields(self, logged_in_page):
        compose = ComposePage(logged_in_page)
        compose.compose(RECEIVER_EMAIL, "TC-01: Full compose test", "Hello! This is an automated test email from Playwright.")
        logger.info("TC-01 PASSED: Email sent successfully")
        logged_in_page.wait_for_timeout(5000)

    # ─────────────────────────────────────────────────────────────
    # TC-02 [POSITIVE] — Send email with subject only (no body)
    # Expected: Proton allows sending with empty body, composer closes
    # ─────────────────────────────────────────────────────────────
    @allure.story("Compose Edge Cases")
    @allure.title("TC-COMP-02: Send email with subject only (empty body)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_send_email_without_body(self, logged_in_page):
        compose = ComposePage(logged_in_page)
        compose.compose(RECEIVER_EMAIL, "TC-01: Full compose test","")

        logger.info("TC-02 PASSED: Email sent without body")

    # ─────────────────────────────────────────────────────────────
    # TC-03 [NEGATIVE] — Send email with no recipient
    # Expected: Proton blocks send & composer stays open
    # ─────────────────────────────────────────────────────────────
    @allure.story("Compose Validation")
    @allure.title("TC-COMP-03: Send email with missing recipient")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.negative
    def test_send_email_without_recipient(self, logged_in_page):
        compose = ComposePage(logged_in_page)
        compose.open_composer()
        # intentionally skip enter_recipient
        compose.enter_subject("TC-03: No recipient test")
        compose.enter_body("This email should NOT be sent.")
        compose.click_send()

        # Proton keeps composer open because recipient is missing
        expect(compose.send_button).to_be_visible(timeout=NAV_TIMEOUT)
        logger.info("TC-03 PASSED: Send blocked correctly when no recipient")
