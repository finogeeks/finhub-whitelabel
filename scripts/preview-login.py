#!/usr/bin/env python3
"""Generate static approximate login brand preview HTML (no network)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from preview_login_lib import write_preview  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate inert brand login preview HTML")
    parser.add_argument("--locale", default="en", help="Locale key from platform-settings (default: en)")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root (default: parent of scripts/)",
    )
    args = parser.parse_args()
    out = write_preview(args.root.resolve(), args.locale)
    print(f"Wrote {out.relative_to(args.root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
