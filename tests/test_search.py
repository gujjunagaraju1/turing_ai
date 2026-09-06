import logging
import allure
import pytest
from playwright.sync_api import Page, expect

from pages.search_page import SearchPage
from config.settings import DEFAULT_TIMEOUT, NAV_TIMEOUT

logger = logging.getLogger(__name__)


@allure.feature("Search & Filter")
@allure.epic("Proton Mail Core")
@pytest.mark.search
class TestSearch:

    # ─────────────────────────────────────────────────────────────
    # TC-SEARCH-01 [POSITIVE] — Search keyword and validate subject contains keyword
    # ─────────────────────────────────────────────────────────────
    @allure.story("Keyword Search")
    @allure.title("TC-SEARCH-01: Search valid keyword and validate subject matches")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    @pytest.mark.regression
    def test_search_valid_keyword_returns_matching_results(self, open_login_url: Page):
        KEYWORD = "test"

        # 1. Login with Receiver (flag=False)
        search = SearchPage(open_login_url, flag=False)
        open_login_url.wait_for_timeout(5000)


        # 2. Type keyword and click search submit
        search.search_for(KEYWORD)
        open_login_url.wait_for_timeout(3000)

        # 3. Validate that the first result subject contains the search keyword
        result_subject = search.get_first_result_subject()
        assert KEYWORD.lower() in result_subject.lower(), (
            f"Expected search result subject to contain '{KEYWORD}', but got: '{result_subject}'"
        )
        logger.info("TC-SEARCH-01 PASSED: Search result subject contains expected keyword")

    # ─────────────────────────────────────────────────────────────
    # TC-SEARCH-02 [NEGATIVE/EDGE] — Search random keyword and verify message list loaded
    # ─────────────────────────────────────────────────────────────
    @allure.story("Keyword Search")
    @allure.title("TC-SEARCH-02: Search random non-matching keyword loads message list cleanly")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_search_random_keyword_loads_message_list(self, open_login_url: Page):
        RANDOM_KEYWORD = "randomxyz999nomatch"

        # 1. Login with Receiver
        search = SearchPage(open_login_url, flag=False)
        open_login_url.wait_for_timeout(5000)

        # 2. Type random keyword and submit search
        search.search_for(RANDOM_KEYWORD)
        open_login_url.wait_for_timeout(3000)

        # 3. Assert message list loaded container is visible
        search.wait_for_message_list_loaded()
        expect(search.message_list_loaded).to_be_visible(timeout=DEFAULT_TIMEOUT)
        logger.info("TC-SEARCH-02 PASSED: Message list loaded correctly for search query")

    # ─────────────────────────────────────────────────────────────
    # TC-SEARCH-03 [POSITIVE] — First fill search text, click clear, submit and verify all mails shown
    # ─────────────────────────────────────────────────────────────
    @allure.story("Search Filter Reset")
    @allure.title("TC-SEARCH-03: Fill search query, clear, submit and verify all emails re-rendered")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_search_clear_and_submit_shows_all_mails(self, open_login_url: Page):
        # 1. Login with Receiver
        search = SearchPage(open_login_url, flag=False)
        open_login_url.wait_for_timeout(5000)

        # 2. First fill search text with keyword
        search.enter_search_text("anyrandomquery123")
        open_login_url.wait_for_timeout(1000)

        # 3. Click Clear button to clear the input
        search.click_clear_search()
        open_login_url.wait_for_timeout(1000)

        # 4. Click Submit search to retrieve all emails
        search.click_submit_search()
        open_login_url.wait_for_timeout(3000)

        # 5. Assert message list is loaded and mails are displayed
        search.wait_for_message_list_loaded()
        mail_count = search.get_result_count()
        assert mail_count >= 1, (
            f"Expected emails to be displayed after clearing search, but found count: {mail_count}"
        )
        logger.info(f"TC-SEARCH-03 PASSED: Search filled, cleared, submitted and {mail_count} emails displayed successfully")
