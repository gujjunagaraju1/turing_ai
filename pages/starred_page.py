import logging
from playwright.sync_api import Page
from config.settings import DEFAULT_TIMEOUT, NAV_TIMEOUT

logger = logging.getLogger(__name__)


class StarredPage:

    # ── LOCATORS ─────────────────────────────────────────────────
    LOC_INBOX_LINK             = "//a[@title='Inbox']"
    LOC_STARRED_LINK           = "//a[@title='Starred']"
    LOC_STAR_BUTTON            = "(//div[@data-shortcut-target='item-container'])[1]//button[@data-testid='message-row:star-button']"
    LOC_STARRED_ITEMS          = "//div[@data-shortcut-target='item-container']"
    LOC_FIRST_STARRED          = "(//div[@data-shortcut-target='item-container'])[1]"
    LOC_FIRST_STARRED_SUBJECT  = "(//div[@data-shortcut-target='item-container'])[1]//span[@data-testid='message-row:subject']"

    # ── CONSTRUCTOR ──────────────────────────────────────────────
    def __init__(self, page: Page):
        self.page                 = page
        self.inbox_link           = page.locator(self.LOC_INBOX_LINK)
        self.starred_link         = page.locator(self.LOC_STARRED_LINK)
        self.star_btn             = page.locator(self.LOC_STAR_BUTTON)
        self.starred_items        = page.locator(self.LOC_STARRED_ITEMS)
        self.first_starred        = page.locator(self.LOC_FIRST_STARRED)
        self.first_starred_subject= page.locator(self.LOC_FIRST_STARRED_SUBJECT)

    # ── ACTIONS ──────────────────────────────────────────────────
    def go_to_inbox(self):
        """Navigate to Inbox folder."""
        self.inbox_link.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.inbox_link.click()
        self.page.wait_for_load_state("domcontentloaded")
        logger.info("Navigated to Inbox")

    def go_to_starred(self):
        """Navigate to Starred folder."""
        self.starred_link.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.starred_link.click()
        self.page.wait_for_load_state("domcontentloaded")
        logger.info("Navigated to Starred folder")

    def star_first_email(self):
        """Click the star button on the first email."""
        self.star_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.star_btn.click()
        logger.info("Clicked star on the first email")

    def unstar_first_email(self):
        """Click the star button again to unstar the first email."""
        self.star_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.star_btn.click()
        logger.info("Unstarred the first email")

    def get_starred_count(self) -> int:
        """Return total visible items in the current view."""
        return self.starred_items.count()

    def get_first_starred_subject(self) -> str:
        """Return the subject text of the first item in the list."""
        self.first_starred_subject.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        return (self.first_starred_subject.text_content() or "").strip()
