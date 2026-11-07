#!/usr/bin/env python3
"""Capture desktop/mobile PNG screenshots of the static brand preview (local file only)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from preview_login_lib import write_preview  # noqa: E402


def capture(root: Path) -> tuple[Path, Path]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise SystemExit("playwright required: pip install playwright && python -m playwright install chromium") from e

    html_path = write_preview(root)
    out_dir = root / "artifacts" / "brand-preview"
    desktop = out_dir / "login-preview-desktop.png"
    mobile = out_dir / "login-preview-mobile.png"
    file_url = html_path.resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(file_url, wait_until="networkidle")
            page.screenshot(path=str(desktop), full_page=True)

            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(file_url, wait_until="networkidle")
            page.screenshot(path=str(mobile), full_page=True)
        finally:
            browser.close()

    return desktop, mobile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    desktop, mobile = capture(root)
    print(f"Wrote {desktop.relative_to(root)}")
    print(f"Wrote {mobile.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
