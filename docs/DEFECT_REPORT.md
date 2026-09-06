# 🐛 Defect & Technical Findings Report

> **Comprehensive Defect Catalog, Synchronization Findings & Edge Case Documentation**  
> *Proton Mail Test Automation Framework*

---

## 📑 Table of Contents
1. [Executive Finding Summary](#1-executive-finding-summary)
2. [Defect Severity Classification](#2-defect-severity-classification)
3. [Deep-Dive Technical Defect Logs](#3-deep-dive-technical-defect-logs)
   - [DEF-01: File Preview Modal Intercepts Header Pointer Events](#def-01-file-preview-modal-intercepts-header-pointer-events)
   - [DEF-02: Sandboxed Rooster Iframe Unreachable via Root DOM](#def-02-sandboxed-rooster-iframe-unreachable-via-root-dom)
   - [DEF-03: Collapsed Search Bar Requires Pre-Activation Focus](#def-03-collapsed-search-bar-requires-pre-activation-focus)
   - [DEF-04: Draft WebSocket Auto-Save Synchronization Latency](#def-04-draft-websocket-auto-save-synchronization-latency)
   - [DEF-05: Localization Variability in Authentication Error Messages](#def-05-localization-variability-in-authentication-error-messages)
4. [Long-Term Quality Recommendations](#4-long-term-quality-recommendations)

---

## 1. Executive Finding Summary

| Defect ID | Component | Summary | Severity | Impact | Status | Framework Fix |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **DEF-01** | E2E / File Preview | Modal overlay blocks top-level Header logout actions | **Medium** | Test Flakiness | **Resolved** | Auto-dismiss preview modal before logout |
| **DEF-02** | Compose / Editor | Message body input unreachable by standard CSS locators | **High** | Blocker | **Resolved** | `frame_locator` with Tab-key fallback |
| **DEF-03** | Search Bar | Search bar does not accept typing without initial click | **Low** | Interaction Failure | **Resolved** | Focus $\rightarrow$ Type $\rightarrow$ Submit flow |
| **DEF-04** | Drafts | Asynchronous WebSocket push delay upon quick composer close | **Medium** | Race Condition | **Resolved** | Explicit state wait on `first_draft` |
| **DEF-05** | Authentication | Password error alert text changes across locales/sessions | **Low** | False Failure | **Resolved** | Resilient substring & error block check |

---

## 2. Defect Severity Classification

- **High:** Blocks automated scenario execution or test path without explicit architectural workaround.
- **Medium:** Causes intermittent race conditions or pointer-event interceptions if timing/modals are unhandled.
- **Low:** Cosmetic or localization variances requiring relaxed assertion patterns.

---

## 3. Deep-Dive Technical Defect Logs

### DEF-01: File Preview Modal Intercepts Header Pointer Events

- **Component:** Mail Viewer $\rightarrow$ Attachment Preview $\rightarrow$ Header Bar
- **Severity:** Medium
- **Allure Story:** Multi-Account Attachment Flow
- **Discovered In:** `tests/test_e2e.py::TestE2E::test_e2e_send_and_receive_mail_with_attachment`
- **Symptom:** After the receiver opens an email with an attachment and previews the file, clicking the user dropdown button `[data-testid='heading:userdropdown']` throws a timeout error because the full-page preview container intercepts pointer events.
- **Observed Error Stack:**
  ```text
  playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
  Call log:
    - waiting for locator("button[data-testid='heading:userdropdown']")
    - locator resolved to <button data-testid="heading:userdropdown">...</button>
    - attempting click action
    - <div class="file-preview-container" data-testid="file-preview">...</div> intercepts pointer events
  ```
- **Root Cause:** The attachment preview modal renders at `z-index: 1000` above the global top-level navigation bar.
- **Resolution in Framework:** Implemented `close_preview_if_open()` in `pages/e2e_page.py` that checks for active preview modals and presses `Escape` before initiating logout:
  ```python
  def close_preview_if_open(self):
      preview = self.page.locator("div[data-testid='file-preview'], .file-preview-container")
      if preview.is_visible():
          self.page.keyboard.press("Escape")
          preview.wait_for(state="hidden", timeout=5000)
  ```

---

### DEF-02: Sandboxed Rooster Iframe Unreachable via Root DOM

- **Component:** Email Composer (`Rooster Editor`)
- **Severity:** High
- **Allure Story:** Compose and Send
- **Discovered In:** `tests/test_compose.py::TestCompose::test_send_email_with_all_fields`
- **Symptom:** Attempts to fill the message body using page-level locators (`self.page.locator("div[contenteditable='true']")`) fail because the element lives in a sandboxed iframe.
- **Root Cause:** Proton Mail embeds its rich text editor inside an external iframe (`rooster-editor`) to isolate HTML/CSS styles and prevent XSS injection.
- **Resolution in Framework:**
  - Implemented `page.frame_locator("//iframe[contains(@class,'rooster')...]")` to target the internal `div[contenteditable='true']`.
  - Added an automatic fallback that switches focus into the body field via keyboard `Tab` navigation if iframe initialization takes longer than usual.

---

### DEF-03: Collapsed Search Bar Requires Pre-Activation Focus

- **Component:** Header Search Bar
- **Severity:** Low
- **Allure Story:** Keyword Search
- **Discovered In:** `tests/test_search.py::TestSearch::test_search_valid_keyword_returns_matching_results`
- **Symptom:** Direct `locator.fill()` on `#global_search` fails because the input is collapsed in an inactive state displaying `"Search messages"`.
- **Root Cause:** The search interface requires a user click event to swap DOM templates and render the expanded search input (`LOC_FILL_SEARCH`).
- **Resolution in Framework:** Updated `SearchPage.enter_search_text()` to execute a clean sequence:
  1. Click search placeholder button.
  2. Wait for expanded input to render in DOM.
  3. Type query with `input.fill(query)`.
  4. Submit search with `input.press("Enter")`.

---

### DEF-04: Draft WebSocket Auto-Save Synchronization Latency

- **Component:** Drafts Folder / Auto-Save Engine
- **Severity:** Medium
- **Allure Story:** Draft Auto-Save
- **Discovered In:** `tests/test_draft.py::TestDraft::test_draft_is_saved_after_close`
- **Symptom:** When the composer close button is clicked, Proton Mail saves the draft in the background via WebSocket. If the test navigates to `//a[@title='Drafts']` immediately, the Drafts list can briefly show 0 items before the server pushes the updated state.
- **Root Cause:** Eventual consistency between client-side composer dismissal and backend mailbox sync.
- **Resolution in Framework:** Added explicit wait `draft.first_draft.wait_for(state="visible", timeout=NAV_TIMEOUT)` before asserting draft count $\ge 1$.

---

### DEF-05: Localization Variability in Authentication Error Messages

- **Component:** Login Page Error Alert
- **Severity:** Low
- **Allure Story:** Negative Authentication
- **Discovered In:** `tests/test_login.py::TestLogin::test_invalid_password`
- **Symptom:** Error banner displays `"The password is not correct"` on English sessions but may return variant wording depending on geo-routing and account lock states.
- **Root Cause:** Dynamic server-side localization strings.
- **Resolution in Framework:** Verified `login.check_error_message()` (asserting the error banner is rendered and visible) combined with a substring assertion for `"The password is not correct"`.

---

## 4. Long-Term Quality Recommendations

1. **Dedicated Test Account State Isolation:** Establish automated pre-test inbox cleanup fixtures to avoid relying on manual email retention in receiver accounts.
2. **Deterministic Data-Testid Selectors:** Recommend development teams standardize `data-testid` attributes across Rooster editor iframe wrappers to eliminate complex XPath selectors.
3. **Mocking Service Worker Updates:** For high-throughput CI runs, configure Chromium context routes to suppress non-essential telemetry and background analytics calls.

