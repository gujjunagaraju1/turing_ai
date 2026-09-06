import logging
from playwright.sync_api import Page
from config.settings import NAV_TIMEOUT, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class ComposePage:

    # ── LOCATORS ─────────────────────────────────────────────────
    LOC_NEW_MESSAGE  = "//button[text()='New message']"
    LOC_SEND_TO      = "//input[@data-testid='composer:to']"
    LOC_SUBJECT_TO   = "//input[@placeholder='Subject']"
    LOC_SUBMIT_MAIL  = "//button[@data-testid='composer:send-button']"
    LOC_MESSAGE_BODY = "//div[@id='rooster-editor']"

    LOC_MESSAGE_SENT_SUCCESSFULLY = "//span[@class='notification__content']"

    # ── CONSTRUCTOR ──────────────────────────────────────────────
    def __init__(self, page: Page):
        self.page            = page
        self.new_message_btn = page.locator(self.LOC_NEW_MESSAGE)
        self.send_to_input   = page.locator(self.LOC_SEND_TO)
        self.subject_input   = page.locator(self.LOC_SUBJECT_TO)
        self.send_button     = page.locator(self.LOC_SUBMIT_MAIL)
        self.message_body    = page.locator(self.LOC_MESSAGE_BODY)
        self.message_sent_successfully = page.locator(self.LOC_MESSAGE_SENT_SUCCESSFULLY)

    # ── ACTIONS ──────────────────────────────────────────────────
    def open_composer(self):
        """Click 'New message' and expand viewport so the composer stays fully visible."""
        self.new_message_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.new_message_btn.click()
        # Expand viewport so compose window isn't clipped at the bottom
       
        logger.info("Compose window opened (viewport → 1920×1080)")

    def enter_recipient(self, email: str):
        """Type the recipient email and press Enter to confirm the address."""
        self.send_to_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.send_to_input.fill(email)
        self.send_to_input.press("Enter")
        logger.info(f"Recipient set to: {email}")

    def enter_subject(self, subject: str):
        """Fill in the subject line."""
        self.subject_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.subject_input.fill(subject)
        logger.info(f"Subject set to: {subject}")

    def enter_body(self, body: str):
        """
        Type content into the Rooster editor.

        Proton Mail renders the editor inside a sandboxed iframe — direct
        page locators cannot reach into iframes. We use frame_locator to
        enter the iframe first, then interact with the contenteditable div.
        Falls back to Tab + keyboard.type() if the iframe isn't found.
        """
        # Primary: Rooster editor lives inside an iframe
        try:
            editor_frame = self.page.frame_locator("//iframe[contains(@class,'rooster') or contains(@title,'composer') or contains(@title,'editor')]")
            editor = editor_frame.locator("div[contenteditable='true'], [role='textbox']")
            editor.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
            editor.first.click()
            editor.first.type(body)
        except Exception:
            # Fallback: Tab from Subject field into body area
            logger.warning("iframe editor not found — falling back to Tab navigation")
            self.subject_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
            self.subject_input.click()
            self.subject_input.press("Tab")
            self.page.wait_for_timeout(400)
            self.page.keyboard.type(body)
        logger.info("Message body filled")

    def click_send(self):
        """Click the Send button to dispatch the email."""
        self.send_button.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        self.send_button.click()
        logger.info("Send button clicked")

    def compose(self, to: str, subject: str, body: str):
        """Full compose flow: open → recipient → subject → body → send → confirm."""
        self.open_composer()
        self.enter_recipient(to)
        self.enter_subject(subject)
        self.enter_body(body)
        self.click_send()
        # Wait for success toast: visible → hidden → then test closes cleanly
        self.message_sent_successfully.wait_for(state="visible", timeout=NAV_TIMEOUT)
        self.message_sent_successfully.wait_for(state="hidden",  timeout=NAV_TIMEOUT)
        logger.info(f"Email composed and sent to {to}")
