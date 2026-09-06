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


class SearchPage:
    LOC_SEARCH_INPUT = "//input[@placeholder='Search messages' or @placeholder='Search date, name, email address, or subject line' or @id='search-keyword']"
    LOC_SEARCH_SUBMIT = "//button[@data-testid='advanced-search:submit']"
    LOC_SEARCH_CLEAR = "//button[@data-testid='advanced-search:clear']"
    LOC_MESSAGE_LIST_LOADED = "//div[@data-testid='message-list-loaded']"
    LOC_MESSAGE_ITEMS = "//div[@data-shortcut-target='item-container']"
    LOC_FIRST_SUBJECT = "(//span[@data-testid='message-row:subject'])[1]"
    LOC_FILL_SEARCH = "//input[@placeholder='Search date, name, email address, or subject line']"

    def __init__(self, page: Page, flag: bool = True):
        self.page = page
        self.flag = flag
        self.search_input = page.locator(self.LOC_SEARCH_INPUT)
        self.search_submit_btn = page.locator(self.LOC_SEARCH_SUBMIT)
        self.search_clear_btn = page.locator(self.LOC_SEARCH_CLEAR)
        self.message_list_loaded = page.locator(self.LOC_MESSAGE_LIST_LOADED)
        self.message_items = page.locator(self.LOC_MESSAGE_ITEMS)
        self.first_subject = page.locator(self.LOC_FIRST_SUBJECT)
        self.fill_search = page.locator(self.LOC_FILL_SEARCH)

        login = LoginPage(page)
        if not flag:
            login.login(RECEIVER_USERNAME, RECEIVER_PASSWORD)
            page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
            logger.info("Logged in as Receiver")
        else:
            login.login(SENDER_USERNAME, SENDER_PASSWORD)
            page.wait_for_url("**/u/**", timeout=NAV_TIMEOUT)
            logger.info("Logged in as Sender")

    def enter_search_text(self, keyword: str):
        self.search_input.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.search_input.first.click()
        self.fill_search.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.fill_search.fill(keyword)
        logger.info(f"Entered search keyword: '{keyword}'")

    def type_search(self, keyword: str):
        self.enter_search_text(keyword)
        self.click_submit_search()
        self.page.wait_for_load_state("domcontentloaded")
        logger.info(f"Filled search input with keyword: '{keyword}' and submitted")

    def click_submit_search(self):
        try:
            if self.search_submit_btn.is_visible():
                self.search_submit_btn.click()
            elif self.fill_search.is_visible():
                self.fill_search.press("Enter")
            else:
                self.search_input.first.press("Enter")
        except Exception:
            try:
                self.fill_search.press("Enter")
            except Exception:
                self.search_input.first.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")
        logger.info("Submitted search")

    def click_clear_search(self):
        try:
            if self.search_clear_btn.is_visible():
                self.search_clear_btn.click()
            elif self.fill_search.is_visible():
                self.fill_search.fill("")
            else:
                self.search_input.first.click()
                self.search_input.first.fill("")
        except Exception:
            try:
                self.fill_search.fill("")
            except Exception:
                self.search_input.first.fill("")
        self.page.wait_for_load_state("domcontentloaded")
        logger.info("Cleared search")

    def search_for(self, keyword: str):
        self.type_search(keyword)

    def get_first_result_subject(self) -> str:
        self.first_subject.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        subject = (self.first_subject.text_content() or "").strip()
        logger.info(f"First search result subject: '{subject}'")
        return subject

    def wait_for_message_list_loaded(self):
        self.message_list_loaded.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        logger.info("Message list loaded container is visible")

    def get_result_count(self) -> int:
        return self.message_items.count()
