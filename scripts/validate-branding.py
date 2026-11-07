#!/usr/bin/env python3
"""Branding + theme validator for finhub-whitelabel (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_branding_lib import print_result, run_validation  # noqa: E402


def main() -> int:
    return print_result(run_validation(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
