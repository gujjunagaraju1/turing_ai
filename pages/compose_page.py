import logging
from playwright.sync_api import Page
from config.settings import NAV_TIMEOUT, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class ComposePage:
    LOC_NEW_MESSAGE = "//button[text()='New message']"
    LOC_SEND_TO = "//input[@data-testid='composer:to']"
    LOC_SUBJECT_TO = "//input[@placeholder='Subject']"
    LOC_SUBMIT_MAIL = "//button[@data-testid='composer:send-button']"
    LOC_MESSAGE_BODY = "//div[@id='rooster-editor']"
    LOC_ATTACHMENT_BTN = "//label[@data-testid='composer:attachment-button']"
    LOC_MESSAGE_SENT_SUCCESSFULLY = "//span[@class='notification__content']"

    def __init__(self, page: Page):
        self.page = page
        self.new_message_btn = page.locator(self.LOC_NEW_MESSAGE)
        self.send_to_input = page.locator(self.LOC_SEND_TO)
        self.subject_input = page.locator(self.LOC_SUBJECT_TO)
        self.send_button = page.locator(self.LOC_SUBMIT_MAIL)
        self.message_body = page.locator(self.LOC_MESSAGE_BODY)
        self.attachment_btn = page.locator(self.LOC_ATTACHMENT_BTN)
        self.message_sent_successfully = page.locator(self.LOC_MESSAGE_SENT_SUCCESSFULLY)

    def open_composer(self):
        self.new_message_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.new_message_btn.click()
        logger.info("Compose window opened")

    def enter_recipient(self, email: str):
        self.send_to_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.send_to_input.fill(email)
        self.send_to_input.press("Enter")
        logger.info(f"Recipient set to: {email}")

    def enter_subject(self, subject: str):
        self.subject_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.subject_input.fill(subject)
        logger.info(f"Subject set to: {subject}")

    def enter_body(self, body: str):
        try:
            editor_frame = self.page.frame_locator("//iframe[contains(@class,'rooster') or contains(@title,'composer') or contains(@title,'editor')]")
            editor = editor_frame.locator("div[contenteditable='true'], [role='textbox']")
            editor.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
            editor.first.click()
            editor.first.type(body)
        except Exception:
            logger.warning("iframe editor not found — falling back to Tab navigation")
            self.subject_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
            self.subject_input.click()
            self.subject_input.press("Tab")
            self.page.wait_for_timeout(400)
            self.page.keyboard.type(body)
        logger.info("Message body filled")

    def click_send(self):
        self.send_button.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.send_button.click()
        logger.info("Send button clicked")

    def attach_file(self, file_path: str):
        try:
            with self.page.expect_file_chooser(timeout=DEFAULT_TIMEOUT) as fc_info:
                self.attachment_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
                self.attachment_btn.click()
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
        except Exception:
            file_input = self.page.locator("//input[@type='file']")
            if file_input.count() > 0:
                file_input.first.set_input_files(file_path)
            else:
                with self.page.expect_file_chooser(timeout=DEFAULT_TIMEOUT) as fc_info:
                    self.attachment_btn.click()
                fc_info.value.set_files(file_path)
        self.page.wait_for_timeout(2000)
        logger.info(f"Attached file: {file_path}")

    def compose(self, to: str, subject: str, body: str):
        self.open_composer()
        self.enter_recipient(to)
        self.enter_subject(subject)
        self.enter_body(body)
        self.click_send()
        self.message_sent_successfully.wait_for(state="visible", timeout=NAV_TIMEOUT)
        self.message_sent_successfully.wait_for(state="hidden", timeout=NAV_TIMEOUT)
        logger.info(f"Email composed and sent to {to}")

    def compose_with_attachment(self, to: str, subject: str, body: str, file_path: str):
        self.open_composer()
        self.enter_recipient(to)
        self.enter_subject(subject)
        self.enter_body(body)
        self.attach_file(file_path)
        self.click_send()
        self.message_sent_successfully.wait_for(state="visible", timeout=NAV_TIMEOUT)
        self.message_sent_successfully.wait_for(state="hidden", timeout=NAV_TIMEOUT)
        logger.info(f"Email with attachment composed and sent to {to}")
