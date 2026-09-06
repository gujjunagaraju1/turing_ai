import logging
from playwright.sync_api import Page
from config.settings import NAV_TIMEOUT, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class DraftPage:

    # ── LOCATORS ─────────────────────────────────────────────────
    LOC_DRAFTS_LINK         = "//a[@title='Drafts']"
    LOC_DRAFT_ITEMS         = "//div[@data-shortcut-target='item-container']"
    LOC_FIRST_DRAFT         = "(//div[@data-shortcut-target='item-container'])[1]"
    LOC_FIRST_DRAFT_SUBJECT = "(//div[@data-shortcut-target='item-container'])[1]//span[@data-testid='message-row:subject']"
    LOC_COMPOSER_SUBJECT    = "//input[@placeholder='Subject']"
    LOC_CLOSE_COMPOSER      = "//button[@data-testid='composer:close-button']"

    # ── CONSTRUCTOR ──────────────────────────────────────────────
    def __init__(self, page: Page):
        self.page                = page
        self.drafts_link         = page.locator(self.LOC_DRAFTS_LINK)
        self.draft_items         = page.locator(self.LOC_DRAFT_ITEMS)
        self.first_draft         = page.locator(self.LOC_FIRST_DRAFT)
        self.first_draft_subject = page.locator(self.LOC_FIRST_DRAFT_SUBJECT)
        self.composer_subject    = page.locator(self.LOC_COMPOSER_SUBJECT)
        self.close_btn           = page.locator(self.LOC_CLOSE_COMPOSER)

    # ── ACTIONS ──────────────────────────────────────────────────
    def close_to_save(self):
        """Click the composer close button — Proton auto-saves as draft."""
        self.close_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.close_btn.click()
        logger.info("Composer closed → draft auto-saved")

    def go_to_drafts(self):
        """Click the Drafts link in the sidebar."""
        self.drafts_link.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.drafts_link.click()
        self.page.wait_for_load_state("domcontentloaded")
        logger.info("Navigated to Drafts folder")

    def draft_count(self) -> int:
        """Return how many draft rows are currently visible."""
        return self.draft_items.count()

    def open_first_draft(self):
        """Click the first draft item to open it in the composer."""
        self.first_draft.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.first_draft.click()
        self.composer_subject.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        logger.info("First draft opened in composer")

    def get_draft_subject(self) -> str:
        """Return the subject text of the first draft directly from the drafts list."""
        self.first_draft_subject.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        return (self.first_draft_subject.text_content() or "").strip()

