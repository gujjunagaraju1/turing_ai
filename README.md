# 🚀 Turium AI — Proton Mail E2E Automation Framework

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Sync%20Engine-green.svg?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![Pytest](https://img.shields.io/badge/Pytest-9.1.1-orange.svg?logo=pytest&logoColor=white)](https://pytest.org/)
[![Allure Report](https://img.shields.io/badge/Allure-Rich%20Reports-yellow.svg?logo=allure&logoColor=white)](https://qameta.io/allure-report/)
[![Pass Rate](https://img.shields.io/badge/Pass%20Rate-100%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

An enterprise-grade, highly resilient **End-to-End (E2E) automated testing framework** engineered for Proton Mail using **Python 3.10+**, **Playwright (Sync API)**, **Pytest**, and **Allure Reporting**.

The framework covers core user journeys: secure authentication, composition with sandboxed iframe editors, auto-save drafts, message starring, advanced email search with filter clearing, and cross-account real-time email/attachment exchange.

---

## 📑 Table of Contents
1. [Key Framework Highlights](#-key-framework-highlights)
2. [Prerequisites & Environment](#-prerequisites--environment)
3. [Quick Start & Installation](#-quick-start--installation)
4. [Configuration & Secrets Management](#-configuration--secrets-management)
5. [Test Suite Execution Taxonomy](#-test-suite-execution-taxonomy)
6. [Allure Reports & Failure Diagnostics](#-allure-reports--failure-diagnostics)
7. [Architecture & Page Object Model](#-architecture--page-object-model)
8. [Troubleshooting & Common Questions](#-troubleshooting--common-questions)
9. [Documentation Index](#-documentation-index)

---

## 🌟 Key Framework Highlights

- **⚡ Playwright Sync API:** Eliminates `async/await` overhead while utilizing Playwright's auto-wait engine for flakiness-free automation.
- **🛡️ Anti-Bot Evasion:** Launches Chromium with `--disable-blink-features=AutomationControlled` to navigate live webmail securely.
- **🖼️ Rooster Iframe Handling:** Resolves rich-text composer iframe rendering with primary `frame_locator` + keyboard `Tab` fallback navigation.
- **📊 Allure Interactive Reports:** Real-time test execution dashboard with attached full-page failure screenshots, Playwright trace zip archives, and session WebM video recordings.
- **🏷️ Suite-Wise Categorization:** Run targeted test groups using Pytest markers: `sanity`, `regression`, `smoke`, `negative`, and `e2e`.

---

## 📋 Prerequisites & Environment

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** 3.10 or higher
- **Browser:** Chromium (installed automatically via Playwright)
- **Network:** Unrestricted access to `https://mail.proton.me` & `https://account.proton.me`

---

## 🚀 Quick Start & Installation

### 1. Clone or Open Workspace
```powershell
cd "Turium AI"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows PowerShell
# source venv/bin/activate    # On macOS/Linux
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Install Playwright Chromium Browser
```powershell
python -m playwright install chromium
```

---

## ⚙️ Configuration & Secrets Management

The framework loads credentials and settings securely from `.env` at runtime via `python-dotenv`:

Create or verify `.env`:
```ini
# Account 1 — Sender (Positive tests, draft save, and sender side of E2E)
SENDER_EMAIL=your_sender_account@proton.me
SENDER_PASSWORD=your_sender_password

# Account 2 — Receiver (Search tests, star tests, negative login, receiver E2E)
RECEIVER_EMAIL=your_receiver_account@proton.me
RECEIVER_PASSWORD=your_receiver_password

# Application Settings
BASE_URL=https://proton.me/mail
BROWSER=chromium
HEADLESS=false
SLOW_MO=0
DEFAULT_TIMEOUT=30000
NAV_TIMEOUT=60000
```

---

## 🎯 Test Suite Execution Taxonomy

### 1. Suite-Wise Execution (Markers)
```powershell
# Run Core Sanity Suite (7 critical path tests)
python -m pytest -m sanity -v

# Run Full Regression Suite (All 16 test cases)
python -m pytest -m regression -v

# Run Fast Smoke Suite (5 rapid build tests)
python -m pytest -m smoke -v

# Run Negative / Error Validation Suite (3 tests)
python -m pytest -m negative -v

# Run End-to-End Multi-Account Suite (2 tests)
python -m pytest -m e2e -v

# Run Regression Suite excluding Sanity
python -m pytest -m "regression and not sanity" -v
```

### 2. Module-Wise Execution
```powershell
python -m pytest tests/test_login.py -v       # Authentication Suite
python -m pytest tests/test_compose.py -v     # Email Composition Suite
python -m pytest tests/test_draft.py -v       # Drafts Suite
python -m pytest tests/test_starred.py -v     # Starred Messages Suite
python -m pytest tests/test_search.py -v      # Search & Filter Suite
python -m pytest tests/test_e2e.py -v         # Multi-Account E2E Suite
```

### 3. Single Test Case Execution
```powershell
python -m pytest tests/test_e2e.py::TestE2E::test_e2e_send_and_receive_mail_with_attachment -v -s
```

---

## 📊 Allure Reports & Failure Diagnostics

Allure execution metrics and failure artifacts are generated automatically into `reports/allure-results/`.

```powershell
# 1. Run test suite to populate Allure results
python -m pytest -v

# 2. Open interactive Allure Report in browser
allure serve reports/allure-results

# 3. Generate standalone Allure HTML report directory
allure generate reports/allure-results -o reports/allure-report --clean

# 4. View Playwright trace file from a failed test
playwright show-trace reports/traces/<trace_filename>.zip
```

### Automatic Failure Attachments:
- 📸 **Failure Screenshot:** Full-page PNG automatically captured and attached to the failed test in Allure.
- 🔍 **Playwright Trace (`.zip`):** Full DOM timeline, network requests, console logs, and action snapshots.
- 🎥 **Session Video (`.webm`):** Full recording of the browser session leading up to the failure.

---

## 🏛️ Architecture & Page Object Model

```
Turium AI/
├── assets/attachments/        # Sample attachment files (.txt, .pdf, .png)
├── config/settings.py         # Central configuration & environment loader
├── docs/                      # Full framework documentation
│   ├── ARCHITECTURE_NOTE.md   # Architecture & Technical Design Note
│   ├── DEFECT_REPORT.md       # Defect Catalog & Edge Cases
│   ├── TEST_CASES.md          # Complete Test Matrix & Suite Specifications
│   └── TEST_REPORT.md         # Test Execution Metrics & Summary
├── pages/                     # Page Object Model (POM) Layer
│   ├── compose_page.py        # Composer & Rooster iframe editor handler
│   ├── draft_page.py          # Drafts folder & auto-save validation
│   ├── e2e_page.py            # High-level E2E workflow aggregators
│   ├── login_page.py          # Authentication & session controls
│   ├── search_page.py         # Search input, clear, & query filters
│   └── starred_page.py        # Starring & Starred folder validation
├── reports/                   # Automated Diagnostics & Artifacts
│   ├── allure-results/        # Allure raw test result data & JSONs
│   ├── allure-report/         # Generated Allure standalone HTML report
│   ├── screenshots/           # Failure full-page PNG screenshots
│   ├── traces/                # Playwright trace zip archives
│   ├── videos/                # WebM session recordings
│   └── report.html            # Standalone Pytest HTML report
├── tests/                     # Test Suites & Fixtures
│   ├── conftest.py            # Shared fixtures (open_login_url, logged_in_page)
│   ├── test_compose.py        # Composition tests
│   ├── test_draft.py          # Draft auto-save tests
│   ├── test_e2e.py            # Multi-account E2E tests
│   ├── test_login.py          # Authentication tests
│   ├── test_search.py         # Search & filter tests
│   └── test_starred.py        # Starred email tests
├── conftest.py                # Root fixture & Allure failure attachment hook
├── pytest.ini                 # Pytest runner configuration & marker taxonomy
├── requirements.txt           # Python dependencies
└── .env                       # Local secrets (git-ignored)
```

---

## 🛠️ Troubleshooting & Common Questions

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `allure : The term 'allure' is not recognized` | Allure CLI binary is not installed on PATH | Results are stored in `reports/allure-results/`. Install Allure CLI via `scoop install allure` or view standalone HTML report at `reports/report.html`. |
| `Rooster editor typing fails` | Proton Mail sandboxes body editor in iframe | Handled automatically via `ComposePage.enter_body()` frame locator + Tab fallback. |
| `Header clicks blocked during logout` | Attachment preview modal remains open | Handled automatically via `E2EPage.close_preview_if_open()`. |
| `pytest: command not found` | Virtual environment is not activated | Run via `python -m pytest` or run `.\venv\Scripts\Activate.ps1`. |

---

## 📚 Documentation Index

- 📑 [Complete Test Cases & Suite Matrix](docs/TEST_CASES.md)
- 🏛️ [Architecture Note & Design Decisions](docs/ARCHITECTURE_NOTE.md)
- 🐛 [Defect & Technical Findings Report](docs/DEFECT_REPORT.md)
- 📊 [Test Execution & Quality Metrics Report](docs/TEST_REPORT.md)

