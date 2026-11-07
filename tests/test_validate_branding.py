"""Automated branding validator tests (positive + negative)."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
import sys

sys.path.insert(0, str(SCRIPTS))

from validate_branding_lib import run_validation  # noqa: E402


@pytest.fixture
def template_copy(tmp_path: Path) -> Path:
    """Minimal repo tree copied from template defaults."""
    for rel in (
        "branding/platform-settings.json",
        "branding/theme-tokens.json",
        "branding/assets/acme-mark.svg",
        "branding/assets/acme-wordmark.svg",
        "branding/assets/favicon.svg",
        "branding/assets/og-acme.svg",
        "persona-templates.json",
        "scripts/brand_validation_limits.json",
    ):
        src = REPO_ROOT / rel
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest)
    return tmp_path


def test_acme_hub_passes(template_copy: Path) -> None:
    result = run_validation(template_copy)
    assert result.ok, [f"{i.code}: {i.message}" for i in result.issues if i.level == "error"]


def test_blank_product_name_fails(template_copy: Path) -> None:
    ps = json.loads((template_copy / "branding/platform-settings.json").read_text())
    ps["product_name"]["en"] = "   "
    (template_copy / "branding/platform-settings.json").write_text(json.dumps(ps))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "blank_locale" for i in result.issues)


def test_title_length_exceeded(template_copy: Path) -> None:
    ps = json.loads((template_copy / "branding/platform-settings.json").read_text())
    ps["auth_login"]["title"]["en"] = "x" * 500
    (template_copy / "branding/platform-settings.json").write_text(json.dumps(ps))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "length_exceeded" for i in result.issues)


def test_html_injection_rejected(template_copy: Path) -> None:
    ps = json.loads((template_copy / "branding/platform-settings.json").read_text())
    ps["family_line"]["en"] = 'Hello <script>alert(1)</script>'
    (template_copy / "branding/platform-settings.json").write_text(json.dumps(ps))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "unsafe_html" for i in result.issues)


def test_path_traversal_in_theme_assets(template_copy: Path) -> None:
    theme = json.loads((template_copy / "branding/theme-tokens.json").read_text())
    theme["assets"]["mark"] = "../../etc/passwd"
    (template_copy / "branding/theme-tokens.json").write_text(json.dumps(theme))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "asset_traversal" for i in result.issues)


def test_missing_asset_path(template_copy: Path) -> None:
    theme = json.loads((template_copy / "branding/theme-tokens.json").read_text())
    theme["assets"]["wordmark"] = "assets/does-not-exist.svg"
    (template_copy / "branding/theme-tokens.json").write_text(json.dumps(theme))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "asset_missing" for i in result.issues)


def test_unsafe_svg_script(template_copy: Path) -> None:
    bad = template_copy / "branding/assets/acme-mark.svg"
    bad.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
        encoding="utf-8",
    )
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "svg_unsafe" for i in result.issues)


def test_low_contrast_theme(template_copy: Path) -> None:
    theme = json.loads((template_copy / "branding/theme-tokens.json").read_text())
    theme["css_variables"]["--ink"] = "#cccccc"
    theme["css_variables"]["--paper"] = "#ffffff"
    (template_copy / "branding/theme-tokens.json").write_text(json.dumps(theme))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "contrast_wcag_aa" for i in result.issues)


def test_malformed_json_fails(template_copy: Path) -> None:
    (template_copy / "branding/platform-settings.json").write_text("{not json")
    result = run_validation(template_copy)
    assert not result.ok


def test_persona_default_count(template_copy: Path) -> None:
    pack = json.loads((template_copy / "persona-templates.json").read_text())
    for t in pack["templates"]:
        t["is_default"] = False
    (template_copy / "persona-templates.json").write_text(json.dumps(pack))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "persona_default" for i in result.issues)


def test_external_logo_url_rejected(template_copy: Path) -> None:
    ps = json.loads((template_copy / "branding/platform-settings.json").read_text())
    ps["logo_url"] = "https://evil.example/logo.svg"
    (template_copy / "branding/platform-settings.json").write_text(json.dumps(ps))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "logo_url_unsafe" for i in result.issues)


def test_malformed_png_rejected(template_copy: Path) -> None:
    png = template_copy / "branding/assets/og-acme.png"
    png.write_bytes(b"not a png file")
    theme = json.loads((template_copy / "branding/theme-tokens.json").read_text())
    theme["assets"]["og"] = "assets/og-acme.png"
    (template_copy / "branding/theme-tokens.json").write_text(json.dumps(theme))
    result = run_validation(template_copy)
    assert not result.ok
    assert any(i.code == "png_invalid" for i in result.issues)


def test_preview_html_escapes_injection(template_copy: Path) -> None:
    from preview_login_lib import build_preview_html

    ps = json.loads((template_copy / "branding/platform-settings.json").read_text())
    ps["product_name"]["en"] = 'Acme <img src=x onerror="x">'
    (template_copy / "branding/platform-settings.json").write_text(json.dumps(ps))
    html = build_preview_html(template_copy)
    assert "<img" not in html or "&lt;img" in html
    assert 'onerror="' not in html
