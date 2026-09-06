import logging
import os
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False

from config.settings import (
    LAUNCH_OPTIONS,
    CONTEXT_OPTIONS,
    DEFAULT_TIMEOUT,
    VIDEOS_DIR,
    TRACES_DIR,
    SCREENSHOTS_DIR,
)

logger = logging.getLogger(__name__)


# =========================================================
# Browser Fixture
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
        # Determine if test failed during setup or call phase
        rep_call = getattr(request.node, "rep_call", None)
        rep_setup = getattr(request.node, "rep_setup", None)
        rep_teardown = getattr(request.node, "rep_teardown", None)
        failed = (
            (rep_call is not None and rep_call.failed) or
            (rep_setup is not None and rep_setup.failed) or
            (rep_teardown is not None and rep_teardown.failed)
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name

        if failed:
            save_failure_artifacts(
                page=page,
                context=context,
                test_name=test_name,
                timestamp=timestamp,
            )
        else:
            # Trace is discarded for passed tests to save disk space
            try:
                context.tracing.stop()
            except Exception as e:
                logger.debug(f"Tracing stop exception: {e}")

        # Retrieve video paths before closing context
        video_paths = get_video_paths(context)

        # Closing context finalizes and flushes video file to disk
        try:
            context.close()
        except Exception as e:
            logger.debug(f"Context close exception: {e}")

        if failed:
            # Attach video to Allure for failed test
            attach_videos_to_allure(video_paths)
        else:
            # Delete video for passed tests to save storage
            delete_videos(video_paths)


# =========================================================
# Failure Artifacts & Allure Attachments
# =========================================================

def save_failure_artifacts(
    page: Page,
    context: BrowserContext,
    test_name: str,
    timestamp: str,
) -> None:
    logger.info(f"Test failed: {test_name} — capturing failure artifacts")

    # -----------------------------------------------------
    # 1. Screenshot
    # -----------------------------------------------------
    screenshot_dir = Path(SCREENSHOTS_DIR)
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshot_dir / f"{test_name}_{timestamp}.png"

    try:
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )
        logger.info(f"Screenshot saved: {screenshot_path}")

        # Attach Screenshot to Allure
        if ALLURE_AVAILABLE and screenshot_path.exists():
            allure.attach.file(
                source=str(screenshot_path),
                name=f"Failure Screenshot ({test_name})",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.info("Failure screenshot attached to Allure report")

    except Exception as e:
        logger.error(f"Screenshot capture/attach failed: {e}")

    # -----------------------------------------------------
    # 2. Playwright Trace
    # -----------------------------------------------------
    trace_dir = Path(TRACES_DIR)
    trace_dir.mkdir(parents=True, exist_ok=True)
    trace_path = trace_dir / f"{test_name}_{timestamp}.zip"

    try:
        context.tracing.stop(
            path=str(trace_path)
        )
        logger.info(f"Trace saved: {trace_path}")

        # Attach Trace to Allure
        if ALLURE_AVAILABLE and trace_path.exists():
            allure.attach.file(
                source=str(trace_path),
                name=f"Playwright Trace Zip ({test_name})",
                attachment_type="application/zip",
                extension="zip",
            )
            logger.info("Playwright trace zip attached to Allure report")

    except Exception as e:
        logger.error(f"Trace capture/attach failed: {e}")


def attach_videos_to_allure(video_paths: list[str]) -> None:
    """Attach finalized video recordings to Allure report for failed tests."""
    if not ALLURE_AVAILABLE:
        return

    for idx, video_path_str in enumerate(video_paths, 1):
        v_path = Path(video_path_str)
        if v_path.exists() and v_path.stat().st_size > 0:
            try:
                allure.attach.file(
                    source=str(v_path),
                    name=f"Test Execution Video {idx if len(video_paths) > 1 else ''}".strip(),
                    attachment_type=allure.attachment_type.WEBM,
                    extension="webm",
                )
                logger.info(f"Video attached to Allure: {v_path.name}")
            except Exception as e:
                logger.error(f"Failed to attach video to Allure: {e}")


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
                logger.warning(f"Could not get video path: {e}")
    return videos


def delete_videos(video_paths: list[str]) -> None:
    for video in video_paths:
        try:
            Path(video).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Video cleanup failed: {e}")


# =========================================================
# Pytest Hooks
# =========================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)