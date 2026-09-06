import time
import logging
import allure
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.compose_page import ComposePage
from pages.starred_page import StarredPage
from pages.e2e_page import E2EPage
from config.settings import (
    BASE_URL,
    ROOT_DIR,
    SENDER_USERNAME,
    SENDER_PASSWORD,
    RECEIVER_EMAIL,
    RECEIVER_USERNAME,
    RECEIVER_PASSWORD,
    DEFAULT_TIMEOUT,
    NAV_TIMEOUT,
)

logger = logging.getLogger(__name__)


@allure.feature("End-to-End Workflow")
@allure.epic("Proton Mail Core")
@pytest.mark.e2e
class TestE2E:

    # ─────────────────────────────────────────────────────────────
    # TC-E2E-01 [POSITIVE] — Sender sends mail -> Logout -> Receiver logs in & checks mail -> Logout
    # ─────────────────────────────────────────────────────────────
    @allure.story("Multi-Account Email Flow")
    @allure.title("TC-E2E-01: End-to-end email transmission and verification across accounts")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    @pytest.mark.regression
    @pytest.mark.smoke
    def test_e2e_send_and_receive_mail(self, open_login_url: Page):
        timestamp = int(time.time())
        subject = f"TC-E2E-01: E2E Mail {timestamp}"
        body = f"Automated E2E test email sent at {timestamp}."

        page = open_login_url
        login = LoginPage(page)
        compose = ComposePage(page)

        # ── Step 1: Login as Sender ──────────────────────────────
        logger.info("Step 1: Logging in as Sender...")
        login.login(SENDER_USERNAME, SENDER_PASSWORD)
        page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        page.wait_for_timeout(3000)

        # ── Step 2: Compose & Send Email to Receiver ─────────────
        logger.info(f"Step 2: Sending email to {RECEIVER_EMAIL}...")
        compose.compose(to=RECEIVER_EMAIL, subject=subject, body=body)
        page.wait_for_timeout(3000)

        # ── Step 3: Logout Sender ────────────────────────────────
        logger.info("Step 3: Logging out Sender...")
        login.logout_user()
        page.wait_for_timeout(2000)

        # ── Step 4: Login as Receiver on Same Screen ─────────────
        logger.info(f"Step 4: Logging in as Receiver ({RECEIVER_USERNAME})...")
        login.login(RECEIVER_USERNAME, RECEIVER_PASSWORD)
        page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        page.wait_for_timeout(5000)

        # ── Step 5: Read & Assert Received Mail in Inbox ─────────
        logger.info("Step 5: Checking received email in Receiver Inbox...")
        subject_locator = page.locator(StarredPage.LOC_SUBJECT_TEXT)
        subject_locator.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        received_subject = (subject_locator.text_content() or "").strip()
        logger.info(f"Receiver received subject: '{received_subject}'")

        clean_sent = "".join(subject.split())
        clean_received = "".join(received_subject.split())

        assert clean_sent in clean_received or clean_received in clean_sent, (
            f"E2E Subject mismatch — Sent: '{subject}', Received: '{received_subject}'"
        )
        logger.info("Mail verified successfully in Receiver inbox")

        # ── Step 6: Logout Receiver ──────────────────────────────
        logger.info("Step 6: Logging out Receiver...")
        login.logout_user()
        logger.info("TC-E2E-01 PASSED: Full E2E Send -> Logout -> Receiver Login -> Check Mail -> Logout completed successfully")

    # ─────────────────────────────────────────────────────────────
    # TC-E2E-02 [POSITIVE] — Sender sends mail with attachment -> Logout -> Receiver logs in, opens mail & downloads attachment -> Logout
    # ─────────────────────────────────────────────────────────────
    @allure.story("Multi-Account Attachment Flow")
    @allure.title("TC-E2E-02: End-to-end attachment sending and receipt verification across accounts")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    @pytest.mark.attachments
    def test_e2e_send_and_receive_mail_with_attachment(self, open_login_url: Page):
        timestamp = int(time.time())
        subject = f"TC-E2E-02: Attachment Mail {timestamp}"
        body = f"Automated E2E email with attachment sent at {timestamp}."

        # Test attachment file
        attachment_file = ROOT_DIR / "assets" / "attachments" / "automation_QA_assemenT_proton.txt"
        if not attachment_file.exists():
            attachment_file.parent.mkdir(parents=True, exist_ok=True)
            attachment_file.write_text("Automation QA Assessment Proton Test File Content")

        page = open_login_url
        login = LoginPage(page)
        compose = ComposePage(page)
        e2e = E2EPage(page)

        # ── Step 1: Login as Sender ──────────────────────────────
        logger.info("Step 1: Logging in as Sender...")
        login.login(SENDER_USERNAME, SENDER_PASSWORD)
        page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        page.wait_for_timeout(3000)

        # ── Step 2: Compose & Send Email with Attachment ─────────
        logger.info(f"Step 2: Sending email with attachment to {RECEIVER_EMAIL}...")
        compose.compose_with_attachment(
            to=RECEIVER_EMAIL,
            subject=subject,
            body=body,
            file_path=str(attachment_file.resolve())
        )
        page.wait_for_timeout(3000)

        # ── Step 3: Logout Sender ────────────────────────────────
        logger.info("Step 3: Logging out Sender...")
        login.logout_user()
        page.wait_for_timeout(2000)

        # ── Step 4: Login as Receiver on Same Screen ─────────────
        logger.info(f"Step 4: Logging in as Receiver ({RECEIVER_USERNAME})...")
        login.login(RECEIVER_USERNAME, RECEIVER_PASSWORD)
        page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
        page.wait_for_timeout(5000)

        # ── Step 5: Read & Assert Received Mail in Inbox ─────────
        logger.info("Step 5: Checking received email in Receiver Inbox...")
        subject_locator = page.locator(StarredPage.LOC_SUBJECT_TEXT)
        subject_locator.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        received_subject = (subject_locator.text_content() or "").strip()
        logger.info(f"Receiver received subject: '{received_subject}'")

        clean_sent = "".join(subject.split())
        clean_received = "".join(received_subject.split())
        assert clean_sent in clean_received or clean_received in clean_sent, (
            f"E2E Subject mismatch — Sent: '{subject}', Received: '{received_subject}'"
        )

        # ── Step 6: Open Email & Verify Attachment is Visible ────
        logger.info("Step 6: Opening email and verifying attachment visibility...")
        e2e.open_first_email()
        assert e2e.is_attachment_visible(), "Attachment is not visible in Receiver's opened email"
        logger.info("Attachment is visible in Receiver's opened email")

        # ── Step 7: Logout Receiver ──────────────────────────────
        logger.info("Step 7: Logging out Receiver...")
        login.logout_user()
        logger.info("TC-E2E-02 PASSED: Full E2E Attachment Send -> Logout -> Receiver Login -> Verify Attachment Visible -> Logout completed successfully")

