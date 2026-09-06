import logging
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from config.settings import (
    LAUNCH_OPTIONS,
    CONTEXT_OPTIONS,
    DEFAULT_TIMEOUT,
    VIDEOS_DIR,
    TRACES_DIR,
)

logger = logging.getLogger(__name__)


# =========================================================
# Browser
# =========================================================

@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Browser:

    browser = playwright.chromium.launch(**LAUNCH_OPTIONS)

    yield browser

    browser.close()


# =========================================================
# Context Factory
# =========================================================

def create_context(
    browser: Browser,
    account: str = "default",
) -> BrowserContext:

    video_dir = Path(VIDEOS_DIR) / account
    video_dir.mkdir(parents=True, exist_ok=True)

    context = browser.new_context(
        **CONTEXT_OPTIONS,
        record_video_dir=str(video_dir),
    )

    context.set_default_timeout(DEFAULT_TIMEOUT)

    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True,
    )

    return context


# =========================================================
# Page Fixture
# =========================================================

@pytest.fixture
def page(browser: Browser, request) -> Page:

    context = create_context(browser)
    page = context.new_page()

    try:
        yield page

    finally:

        report = getattr(request.node, "rep_call", None)
        failed = report is not None and report.failed

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if failed:
            save_failure_artifacts(
                page=page,
                context=context,
                test_name=request.node.name,
                timestamp=timestamp,
            )
        else:
            # Trace is discarded
            context.tracing.stop()

        # Get video path before closing context
        video_paths = get_video_paths(context)

        # Closing context finalizes video
        context.close()

        # Delete video for passed test
        if not failed:
            delete_videos(video_paths)


# =========================================================
# Failure Artifacts
# =========================================================

def save_failure_artifacts(
    page: Page,
    context: BrowserContext,
    test_name: str,
    timestamp: str,
) -> None:

    logger.info(f"Test failed: {test_name}")

    # -----------------------------------------------------
    # Screenshot
    # -----------------------------------------------------

    screenshot_dir = Path(TRACES_DIR).parent / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    screenshot_path = (
        screenshot_dir /
        f"{test_name}_{timestamp}.png"
    )

    try:
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        logger.info(f"Screenshot saved: {screenshot_path}")

    except Exception as e:
        logger.error(f"Screenshot failed: {e}")

    # -----------------------------------------------------
    # Trace
    # -----------------------------------------------------

    trace_dir = Path(TRACES_DIR)
    trace_dir.mkdir(parents=True, exist_ok=True)

    trace_path = (
        trace_dir /
        f"{test_name}_{timestamp}.zip"
    )

    try:
        context.tracing.stop(
            path=str(trace_path)
        )

        logger.info(f"Trace saved: {trace_path}")

    except Exception as e:
        logger.error(f"Trace failed: {e}")


# =========================================================
# Video Helpers
# =========================================================

def get_video_paths(context: BrowserContext) -> list[str]:

    videos = []

    for page in context.pages:

        if page.video:

            try:
                videos.append(page.video.path())

            except Exception as e:
                logger.warning(
                    f"Could not get video path: {e}"
                )

    return videos


def delete_videos(video_paths: list[str]) -> None:

    for video in video_paths:

        try:
            Path(video).unlink(missing_ok=True)

        except Exception as e:
            logger.warning(
                f"Video cleanup failed: {e}"
            )


# =========================================================
# Pytest Hook
# =========================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        item.rep_call = report