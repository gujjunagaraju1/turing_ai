import logging
from playwright.sync_api import Page, expect

from pages.compose_page import ComposePage
from pages.draft_page import DraftPage
from config.settings import NAV_TIMEOUT

logger = logging.getLogger(__name__)


class TestDraft:

    # ─────────────────────────────────────────────────────────────
    # TC-DRAFT-01 [POSITIVE] — Draft saved after closing composer
    # ─────────────────────────────────────────────────────────────
    def test_draft_is_saved_after_close(self, logged_in_page):
        SUBJECT = "TC-DRAFT-01: Auto-save draft"

        compose = ComposePage(logged_in_page)
        draft   = DraftPage(logged_in_page)

        # 1. Click "New message"  → LOC_NEW_MESSAGE = "//button[text()='New message']"
        compose.open_composer()

        # 2. Fill Subject         → LOC_SUBJECT_TO  = "//input[@placeholder='Subject']"
        compose.enter_subject(SUBJECT)

        # 3. Click Close          → LOC_CLOSE_COMPOSER = "//button[@data-testid='composer:close-button']"
        draft.close_to_save()

        # 4. Open Drafts          → LOC_DRAFTS_LINK = "//a[@title='Drafts']"
        draft.go_to_drafts()


        # 5. Assert first draft exists  → LOC_FIRST_DRAFT = "(//div[@data-shortcut-target='item-container'])[1]"
        draft.first_draft.wait_for(state="visible", timeout=NAV_TIMEOUT)
        assert draft.draft_count() >= 1, "Expected at least 1 draft in Drafts folder"
        logger.info("TC-DRAFT-01 PASSED: Draft saved and visible in Drafts folder")

    # ─────────────────────────────────────────────────────────────
    # TC-DRAFT-02 [POSITIVE] — Draft subject persists after saving
    # ─────────────────────────────────────────────────────────────
    def test_draft_subject_persists(self, logged_in_page):
        logged_in_page.wait_for_timeout(3000)
        SUBJECT = "TC-DRAFT-02: Subject persistence check"

        compose = ComposePage(logged_in_page)
        draft   = DraftPage(logged_in_page)

        # 1. Click "New message"  → LOC_NEW_MESSAGE = "//button[text()='New message']"
        compose.open_composer()

        # 2. Fill Subject         → LOC_SUBJECT_TO  = "//input[@placeholder='Subject']"
        compose.enter_subject(SUBJECT)

        # 3. Click Close          → LOC_CLOSE_COMPOSER = "//button[@data-testid='composer:close-button']"
        draft.close_to_save()

        # 4. Open Drafts          → LOC_DRAFTS_LINK = "//a[@title='Drafts']"
        draft.go_to_drafts()

        logged_in_page.wait_for_timeout(2000)


        # 5. Read first draft subject directly → LOC_FIRST_DRAFT_SUBJECT = "(//div[@data-shortcut-target='item-container'])[1]//span[@data-testid='message-row:subject']"
        saved_subject = draft.get_draft_subject()
        assert saved_subject == SUBJECT, (
            f"Subject mismatch — expected: '{SUBJECT}', got: '{saved_subject}'"
        )
        logger.info("TC-DRAFT-02 PASSED: Draft subject persists correctly")

