import logging
from playwright.sync_api import Page, expect

from pages.starred_page import StarredPage
from config.settings import DEFAULT_TIMEOUT, NAV_TIMEOUT

logger = logging.getLogger(__name__)


class TestStarred:

    # ─────────────────────────────────────────────────────────────
    # TC-STAR-01 [POSITIVE] — Star an email from Inbox & verify in Starred folder
    # ─────────────────────────────────────────────────────────────
    def test_star_email_visible_in_starred_folder(self, receiver_logged_in_page):
        starred = StarredPage(receiver_logged_in_page)

        # 1. Open Inbox
        starred.go_to_inbox()

        # 2. Get subject of first email to star
        expected_subject = starred.get_first_starred_subject()
        logger.info(f"Starring email with subject: '{expected_subject}'")

        # 3. Star first email
        starred.star_first_email()

        # 4. Navigate to Starred folder
        starred.go_to_starred()

        # 5. Assert the email appears in Starred folder
        starred.first_starred.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        actual_subject = starred.get_first_starred_subject()

        assert actual_subject == expected_subject, (
            f"Starred subject mismatch — expected: '{expected_subject}', got: '{actual_subject}'"
        )
        logger.info("TC-STAR-01 PASSED: Starred email appears in Starred folder")

    # ─────────────────────────────────────────────────────────────
    # TC-STAR-02 [POSITIVE] — Unstar email & verify removed from Starred folder
    # ─────────────────────────────────────────────────────────────
    def test_unstar_email_removes_from_starred(self, receiver_logged_in_page):
        starred = StarredPage(receiver_logged_in_page)

        # 1. Navigate to Starred folder
        starred.go_to_starred()

        # 2. Unstar the first email
        initial_count = starred.get_starred_count()
        starred.unstar_first_email()

        # 3. Small wait for state transition / reload Starred
        starred.page.wait_for_timeout(2000)

        # 4. Verify count decreases or empty
        new_count = starred.get_starred_count()
        assert new_count < initial_count, (
            f"Expected starred count to decrease. Initial: {initial_count}, Now: {new_count}"
        )
        logger.info("TC-STAR-02 PASSED: Unstarred email successfully removed from Starred folder")
