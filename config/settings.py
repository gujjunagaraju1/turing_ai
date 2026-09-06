# ═══════════════════════════════════════════════════════════════
# config/settings.py — Central Configuration & Environment Loader
# ═══════════════════════════════════════════════════════════════
#
# WHAT THIS FILE DOES:
#   1. Reads the .env file using python-dotenv
#   2. Exposes all config values as typed Python constants
#   3. Acts as a SINGLE SOURCE OF TRUTH for all test configuration
#
# JAVA EQUIVALENT:
#   Like a ConfigReader.java that reads config.properties file
#   Properties prop = new Properties();
#   prop.load(new FileInputStream("config.properties"));
#
# HOW TO USE IN TESTS:
#   from config.settings import SENDER_EMAIL, BASE_URL, DEFAULT_TIMEOUT
# ───────────────────────────────────────────────────────────────

import os
from pathlib import Path
from dotenv import load_dotenv

# ── LOAD .env FILE ───────────────────────────────────────────────
# Path(__file__) = current file location (config/settings.py)
# .parent        = config/ folder
# .parent        = project root (Turium AI/)
# So we always find .env regardless of where pytest is run from

ROOT_DIR = Path(__file__).parent.parent   # Project root directory
ENV_FILE = ROOT_DIR / ".env"              # Full path to .env file

# load_dotenv reads .env and puts values into os.environ
# override=True means .env values override existing system env vars
load_dotenv(dotenv_path=ENV_FILE, override=True)


# ═══════════════════════════════════════════════════════════════
# ACCOUNT CREDENTIALS
# ═══════════════════════════════════════════════════════════════
# Accepts username-only (e.g. gujjunagaraju) or full email from .env.
# Appends @proton.me if no @ present; extracts username from full email.

_raw_sender   = os.getenv("SENDER_EMAIL", "").strip()
_raw_receiver = os.getenv("RECEIVER_EMAIL", "").strip()

# Sender account — Account 1 (sends email in 2-account tests)
SENDER_EMAIL: str    = _raw_sender if "@" in _raw_sender else f"{_raw_sender}@proton.me"
SENDER_USERNAME: str = SENDER_EMAIL.split("@")[0]
SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "")

# Receiver account — Account 2 (receives email in 2-account tests)
RECEIVER_EMAIL: str    = _raw_receiver if "@" in _raw_receiver else f"{_raw_receiver}@proton.me"
RECEIVER_USERNAME: str = RECEIVER_EMAIL.split("@")[0]
RECEIVER_PASSWORD: str = os.getenv("RECEIVER_PASSWORD", "")


# ═══════════════════════════════════════════════════════════════
# APPLICATION URLS
# ═══════════════════════════════════════════════════════════════

BASE_URL: str = os.getenv("BASE_URL", "https://proton.me/mail")
MAIL_URL: str = "https://mail.proton.me"


# ═══════════════════════════════════════════════════════════════
# BROWSER SETTINGS
# ═══════════════════════════════════════════════════════════════

# Browser type: chromium | firefox | webkit
BROWSER: str = os.getenv("BROWSER", "chromium")

# Headless mode: True = no browser window (use in CI/CD)
HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"

# Slow motion: delay between actions in ms (0 = full speed)
# Set to 500 to watch tests run in slow motion for debugging
SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))


# ═══════════════════════════════════════════════════════════════
# TIMEOUT SETTINGS (all values in milliseconds)
# ═══════════════════════════════════════════════════════════════

# Default timeout for locating & interacting with elements
DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))  # 30 seconds

# Extra time for heavy async operations (e.g., email delivery, undo-send)
ASYNC_TIMEOUT: int = 45000   # 45 seconds

# Short timeout for elements that should appear immediately
SHORT_TIMEOUT: int = 5000    # 5 seconds

# Navigation timeout for full page loads
NAV_TIMEOUT: int = 60000     # 60 seconds


# ═══════════════════════════════════════════════════════════════
# BROWSER LAUNCH OPTIONS (passed to playwright browser.launch())
# ═══════════════════════════════════════════════════════════════

# These are passed directly to playwright when launching browser
# Like ChromeOptions in Selenium Java
LAUNCH_OPTIONS: dict = {
    "headless": HEADLESS,
    "slow_mo": SLOW_MO,
    "args": [
        "--disable-blink-features=AutomationControlled",  # avoid bot detection
        "--no-sandbox",                                    # needed in CI/Linux
    ]
}

# Browser context options (viewport, locale, timezone)
CONTEXT_OPTIONS: dict = {
    "viewport": None,# expanded so compose window is never clipped
    "locale": "en-US",
    "timezone_id": "Asia/Kolkata",
    "accept_downloads": True,                     # needed for attachment download tests
}


# ═══════════════════════════════════════════════════════════════
# DIRECTORIES (auto-creates folders if they don't exist)
# ═══════════════════════════════════════════════════════════════

REPORTS_DIR = ROOT_DIR / "reports"
VIDEOS_DIR  = REPORTS_DIR / "videos"
TRACES_DIR  = REPORTS_DIR / "traces"
ASSETS_DIR  = ROOT_DIR / "assets" / "attachments"

# Create directories if they don't exist (like mkdir -p)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
TRACES_DIR.mkdir(parents=True, exist_ok=True)


