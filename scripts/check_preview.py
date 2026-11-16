"""Open the generated preview in Chromium and verify every remote image loads.

Usage:
    python scripts/check_preview.py
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
PREVIEW = BASE_DIR / "preview-blog.html"
SHOT = BASE_DIR / "preview-shot.png"

IMAGE_STATE_JS = """
() => Array.from(document.images).map(function (img) {
  return {
    name: img.src.split('/').pop(),
    width: img.naturalWidth,
    height: img.naturalHeight,
    complete: img.complete
  };
})
"""


def main() -> int:
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Exception:
            browser = playwright.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(PREVIEW.resolve().as_uri(), wait_until="load")
        page.wait_for_timeout(6000)
        rows = page.evaluate(IMAGE_STATE_JS)
        for row in rows:
            print(
                "%-34s %4dx%-4d complete=%s"
                % (row["name"], row["width"], row["height"], row["complete"])
            )
        loaded = sum(1 for row in rows if row["width"] > 0)
        print("images: %d, loaded: %d" % (len(rows), loaded))
        page.screenshot(path=str(SHOT))
        print("screenshot: %s" % SHOT)
        browser.close()
    return 0 if rows and loaded == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
