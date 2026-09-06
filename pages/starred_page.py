import logging
from playwright.sync_api import Page
from config.settings import (
    DEFAULT_TIMEOUT,
    NAV_TIMEOUT,
    SENDER_USERNAME,
    SENDER_PASSWORD,
    RECEIVER_USERNAME,
    RECEIVER_PASSWORD,
)
from pages.login_page import LoginPage

logger = logging.getLogger(__name__)


class StarredPage:
    LOC_STAR_BUTTON = "(//button[@data-testid='item-star-false'])[1]"
    LOC_SUBJECT_TEXT = "(//span[@data-testid='message-row:subject'])[1]"
    LOC_STAR_SECTION = "//a[@title='Starred']"
    LOC_FIRST_TEXT_FROM_STARITEMS = "(//div[@data-shortcut-target='item-container'])[1]//span[@data-testid='message-row:subject']"

    def __init__(self, page: Page, flag: bool = True):
        self.page = page
        self.flag = flag
        self.star_btn = page.locator(self.LOC_STAR_BUTTON)
        self.subject_text = page.locator(self.LOC_SUBJECT_TEXT)
        self.star_section = page.locator(self.LOC_STAR_SECTION)
        self.first_text_from_staritems = page.locator(self.LOC_FIRST_TEXT_FROM_STARITEMS)

        login = LoginPage(page)
        if not flag:
            login.login(RECEIVER_USERNAME, RECEIVER_PASSWORD)
            page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
            logger.info("Logged in as Receiver")
        else:
            login.login(SENDER_USERNAME, SENDER_PASSWORD)
            page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
            logger.info("Logged in as Sender")

    def get_subject_text(self) -> str:
        self.subject_text.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        subject = (self.subject_text.text_content() or "").strip()
        logger.info(f"Copied subject text: '{subject}'")
        return subject

    def click_star(self):
        self.star_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.star_btn.click()
        logger.info("Clicked on star button")

    def go_to_starred_section(self):
        self.star_section.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.star_section.click()
        self.page.wait_for_load_state("domcontentloaded")
        logger.info("Navigated to Starred section")

    def get_first_text_from_staritems(self) -> str:
        self.first_text_from_staritems.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        return (self.first_text_from_staritems.text_content() or "").strip()
