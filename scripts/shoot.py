"""Generate blog screenshots and a demo video against the running dev server.

Run the Flask server first, then:
    python scripts/shoot.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from openpyxl import Workbook
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
SHOTS_DIR = BASE_DIR / "screenshots"
SAMPLES_DIR = BASE_DIR / "samples"
URL = "http://127.0.0.1:5000"


def ensure_import_sample() -> Path:
    SAMPLES_DIR.mkdir(exist_ok=True)
    path = SAMPLES_DIR / "import-demo.xlsx"
    if path.exists():
        return path
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contacts"
    sheet.append(
        [
            "Name",
            "Company",
            "Title",
            "Notes",
            "Favorite",
            "Phone 1",
            "Phone 2",
            "Email 1",
            "WeChat 1",
            "Address 1",
            "Other 1",
        ]
    )
    sheet.append(
        [
            "Henry Zhao",
            "Fuzhou University",
            "Lab Supervisor",
            "Introduced the Excel review checklist.",
            "Yes",
            "13800000011",
            "0592-0000011",
            "henry.zhao@example.edu",
            "henry_zhao_fzu",
            "Building 3, Room 301",
            "https://example.com/henry",
        ]
    )
    sheet.append(
        [
            "Ivy Sun",
            "Maynooth University",
            "Exchange Student",
            "",
            "No",
            "13800000012",
            "",
            "ivy.sun@example.edu",
            "",
            "",
            "",
        ]
    )
    sheet.append(
        [
            "Grace Wang",
            "Logistics Lab",
            "",
            "Imported again to show the merge rule.",
            "Yes",
            "13800000013",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    workbook.save(path)
    return path


def main() -> int:
    SHOTS_DIR.mkdir(exist_ok=True)
    video_dir = SHOTS_DIR / "video"
    if video_dir.exists():
        shutil.rmtree(video_dir)
    video_dir.mkdir(parents=True)
    import_file = ensure_import_sample()

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Exception:
            browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1280, "height": 900},
        )
        page = context.new_page()

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(SHOTS_DIR / "01-home.png"))

        page.click("#btn-favorites")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(SHOTS_DIR / "02-favorites-filter.png"))
        page.click("#btn-favorites")
        page.wait_for_timeout(700)

        page.click("#btn-new")
        page.wait_for_timeout(600)
        page.fill("#f-name", "Fiona Zhang")
        page.fill("#f-company", "Fuzhou University")
        page.fill("#f-title", "Teaching Assistant")
        page.fill("#f-notes", "Reviews the Excel import template every Friday.")
        page.fill(".method-row .m-label", "mobile")
        page.fill(".method-row .m-value", "13800000021")
        page.click("#btn-add-method")
        page.wait_for_timeout(300)
        rows = page.locator(".method-row")
        rows.nth(1).locator(".m-kind").select_option("email")
        rows.nth(1).locator(".m-label").fill("work")
        rows.nth(1).locator(".m-value").fill("fiona.zhang@example.edu")
        page.wait_for_timeout(600)
        page.screenshot(path=str(SHOTS_DIR / "03-new-contact-dialog.png"))

        page.click("#btn-save")
        page.wait_for_timeout(900)
        page.screenshot(path=str(SHOTS_DIR / "04-contact-saved.png"))

        page.fill("#search", "13800000021")
        page.wait_for_timeout(900)
        page.screenshot(path=str(SHOTS_DIR / "05-search-by-phone.png"))
        page.fill("#search", "")
        page.wait_for_timeout(800)

        page.set_input_files("#import-input", str(import_file))
        page.wait_for_timeout(1600)
        page.screenshot(path=str(SHOTS_DIR / "06-import-result.png"))

        with page.expect_download() as download_info:
            page.click("#btn-export")
        download = download_info.value
        download.save_as(str(SHOTS_DIR / "exported-contacts.xlsx"))
        page.wait_for_timeout(1500)
        page.screenshot(path=str(SHOTS_DIR / "07-after-export.png"))

        video_path = page.video.path()
        context.close()
        browser.close()

    target = SHOTS_DIR / "demo-run.webm"
    if video_path and Path(video_path).exists():
        shutil.move(video_path, target)
        print("Video: %s" % target)
    print("Screenshots written to %s" % SHOTS_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
