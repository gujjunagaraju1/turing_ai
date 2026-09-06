import logging
import allure
import pytest
from playwright.sync_api import Page, expect

from pages.starred_page import StarredPage
from config.settings import DEFAULT_TIMEOUT, NAV_TIMEOUT

logger = logging.getLogger(__name__)


@allure.feature("Starred Messages")
@allure.epic("Proton Mail Core")
@pytest.mark.starred
@pytest.mark.inbox
class TestStarred:

    # ─────────────────────────────────────────────────────────────
    # TC-STAR-01 [POSITIVE] — Star an email and assert in Starred section
    # ─────────────────────────────────────────────────────────────
    @allure.story("Star Email")
    @allure.title("TC-STAR-01: Star email and verify presence in Starred section")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    @pytest.mark.regression
    def test_star_email_visible_in_starred_section(self, open_login_url):
        # 1. Login as receiver (flag=False)
        starred = StarredPage(open_login_url, flag=False)
        open_login_url.wait_for_timeout(5000)

        # 2. Copy subject text
        copied_subject = starred.get_subject_text()

        # 3. Click on star
        starred.click_star()
        open_login_url.wait_for_timeout(2000)

        # 4. Click on Starred section
        starred.go_to_starred_section()


        # 5. Assert the first subject in Starred section contains copied subject (ignoring spaces/whitespace)
        starred_subject = starred.get_first_text_from_staritems()
        
        # Normalize by removing spaces/whitespace for comparison
        clean_copied = "".join(copied_subject.split())
        clean_starred = "".join(starred_subject.split())

        assert clean_copied in clean_starred, (
            f"Subject mismatch in Starred section — expected '{clean_copied}' in '{clean_starred}'"
        )
        logger.info("TC-STAR-01 PASSED: Copied subject matches first item in Starred section")

