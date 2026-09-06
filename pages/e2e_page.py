import logging
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.compose_page import ComposePage
from pages.starred_page import StarredPage
from config.settings import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class E2EPage:
    LOC_FIRST_MESSAGE_ROW = "(//div[@data-shortcut-target='item-container'])[1] | (//span[@data-testid='message-row:subject'])[1]"
    LOC_ATTACHMENT_ITEM = (
        "//div[@data-testid='attachment-item'] | "
        "//button[@data-testid='attachment-thumbnail'] | "
        "//div[@data-testid='file-preview'] | "
        "//div[contains(@class, 'attachment')] | "
        "//span[contains(text(), 'automation_QA_assemenT_proton')]"
    )
    LOC_ATTACHMENT_DOWNLOAD = (
        "//div[@data-testid='file-preview']//button[@data-testid='file-preview:download' or @title='Download' or contains(@aria-label, 'Download') or contains(@data-testid, 'download')] | "
        "//button[@data-testid='file-preview:download'] | "
        "//button[@data-testid='attachment-item:download'] | "
        "//button[@title='Download' or @aria-label='Download' or contains(@aria-label, 'Download')]"
    )

    def __init__(self, page: Page):
        self.page = page
        self.login_page = LoginPage(page)
        self.compose_page = ComposePage(page)

    def login_as_sender(self, username: str, password: str):
        self.login_page.login(username, password)

    def send_mail(self, to: str, subject: str, body: str):
        self.compose_page.compose(to=to, subject=subject, body=body)

    def send_mail_with_attachment(self, to: str, subject: str, body: str, file_path: str):
        self.compose_page.compose_with_attachment(to=to, subject=subject, body=body, file_path=file_path)

    def logout(self):
        self.login_page.logout_user()

    def get_received_mail_subject(self) -> str:
        starred_page = StarredPage(self.page, flag=False)
        return starred_page.get_subject_text()

    def open_first_email(self):
        row = self.page.locator(self.LOC_FIRST_MESSAGE_ROW).first
        row.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        row.click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        logger.info("Opened first email in inbox")

    def close_preview_if_open(self):
        try:
            close_btn = self.page.locator("//button[@data-testid='file-preview:close' or @title='Close' or contains(@aria-label, 'Close')]").first
            if close_btn.is_visible():
                close_btn.click()
            else:
                self.page.keyboard.press("Escape")
        except Exception:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(1000)
        logger.info("Closed preview modal if open")

    def is_attachment_visible(self) -> bool:
        attachment = self.page.locator(self.LOC_ATTACHMENT_ITEM).first
        attachment.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        is_vis = attachment.is_visible()
        logger.info(f"Attachment visible in receiver email: {is_vis}")
        return is_vis

    def download_attachment(self, save_path: str = None) -> str:
        download_btn = self.page.locator(self.LOC_ATTACHMENT_DOWNLOAD).first
        download_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        with self.page.expect_download(timeout=DEFAULT_TIMEOUT) as download_info:
            try:
                download_btn.click()
            except Exception:
                download_btn.click(force=True)
        download = download_info.value
        if save_path:
            download.save_as(save_path)
            logger.info(f"Attachment saved to: {save_path}")
            self.close_preview_if_open()
            return save_path
        tmp_path = download.path()
        logger.info(f"Attachment downloaded: {download.suggested_filename}")
        self.close_preview_if_open()
        return tmp_path
