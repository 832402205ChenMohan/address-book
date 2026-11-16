"""Render docs/BLOG-en.md into a standalone HTML preview (preview-blog.html).

Usage:
    python scripts/build_preview.py
"""

from __future__ import annotations

from pathlib import Path

import markdown

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE = BASE_DIR / "docs" / "BLOG-en.md"
TARGET = BASE_DIR / "preview-blog.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{
    margin: 0; background: #f6f8f8; color: #14211f;
    font: 16px/1.72 "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  }}
  .page {{
    max-width: 880px; margin: 32px auto 64px; padding: 48px 56px;
    background: #fff; border: 1px solid #e5ebea; border-radius: 14px;
    box-shadow: 0 12px 40px rgba(16, 42, 38, .07);
  }}
  h1 {{ font-size: 30px; line-height: 1.3; margin: 0 0 18px; }}
  h2 {{ font-size: 22px; margin: 40px 0 14px; padding-bottom: 8px; border-bottom: 1px solid #edf1f0; }}
  h3 {{ font-size: 18px; margin: 26px 0 10px; color: #0b5c56; }}
  p, li {{ color: #223330; }}
  blockquote {{
    margin: 16px 0; padding: 12px 18px; border-left: 4px solid #0f766e;
    background: #f4faf8; color: #3b5450; border-radius: 0 8px 8px 0;
  }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14.5px; }}
  th, td {{ border: 1px solid #e2e8e6; padding: 8px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #f2f7f5; font-weight: 700; }}
  code {{ background: #f3f7f6; padding: 1px 5px; border-radius: 4px; font-size: 13.5px; }}
  pre {{ background: #0e2523; color: #e8f5f1; padding: 14px 18px; border-radius: 10px; overflow-x: auto; }}
  pre code {{ background: none; color: inherit; }}
  img {{ max-width: 100%; height: auto; display: block; margin: 12px 0; border: 1px solid #e2e8e6; border-radius: 10px; }}
  a {{ color: #0b5c56; }}
  hr {{ border: none; border-top: 1px solid #edf1f0; margin: 32px 0; }}
  .badge {{ display: inline-block; background: #eaf6f2; color: #0b5c56; border-radius: 6px; padding: 2px 8px; font-size: 12px; }}
</style>
</head>
<body>
<div class="page">
{body}
</div>
</body>
</html>
"""


def main() -> int:
    source_text = SOURCE.read_text(encoding="utf-8")
    body = markdown.markdown(
        source_text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )
    title = source_text.splitlines()[0].lstrip("# ").strip()
    TARGET.write_text(
        TEMPLATE.format(title=title, body=body), encoding="utf-8"
    )
    print("preview written: %s (%d bytes)" % (TARGET, TARGET.stat().st_size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
