"""Shared branding validation and theme helpers (no network)."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

LOCALE_KEYS = ("en",)
REQUIRED_LOCALE_KEYS = ("en",)

UNSAFE_HTML_PATTERN = re.compile(
    r"<\s*(script|iframe|object|embed|form)\b|on\w+\s*=|javascript:",
    re.IGNORECASE,
)

UNSAFE_SVG_TAGS = frozenset(
    {"script", "foreignObject", "iframe", "object", "embed", "animate", "set"}
)
UNSAFE_SVG_ATTR_PREFIXES = ("on",)
UNSAFE_HREF_SCHEMES = re.compile(r"^\s*(javascript|data|http|https):", re.I)

HEX_COLOR = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


@dataclass
class ValidationIssue:
    level: str  # error | warn
    code: str
    message: str


@dataclass
class BrandValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)

    def add(self, level: str, code: str, message: str) -> None:
        self.issues.append(ValidationIssue(level, code, message))


def load_limits(root: Path) -> dict[str, Any]:
    path = root / "scripts" / "brand_validation_limits.json"
    if not path.is_file():
        raise FileNotFoundError(f"Missing limits file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_non_blank_localized(
    result: BrandValidationResult,
    obj: dict[str, Any] | None,
    field_path: str,
    locales: tuple[str, ...] = REQUIRED_LOCALE_KEYS,
) -> None:
    if not isinstance(obj, dict):
        result.add("error", "schema_missing", f"{field_path}: expected localized object")
        return
    for loc in locales:
        val = obj.get(loc)
        if val is None or not str(val).strip():
            result.add("error", "blank_locale", f"{field_path}.{loc}: required non-blank string")


def check_length(
    result: BrandValidationResult,
    value: str,
    field_path: str,
    max_len: int,
) -> None:
    if len(value) > max_len:
        result.add(
            "error",
            "length_exceeded",
            f"{field_path}: length {len(value)} exceeds documented limit {max_len}",
        )


def check_no_html_injection(result: BrandValidationResult, value: str, field_path: str) -> None:
    if UNSAFE_HTML_PATTERN.search(value):
        result.add("error", "unsafe_html", f"{field_path}: rejected unsafe HTML/script patterns")


def is_safe_logo_path(logo_url: str) -> bool:
    if not logo_url or not isinstance(logo_url, str):
        return False
    if logo_url.startswith(("http://", "https://", "//")):
        return False
    if ".." in logo_url.split("/"):
        return False
    if not logo_url.startswith("/"):
        return False
    return True


def resolve_logo_file(root: Path, logo_url: str, theme_assets: dict[str, str]) -> Path | None:
    """Map platform logo_url to a local branding file when possible."""
    if not logo_url:
        return None
    tail = Path(logo_url).name
    candidates = [
        root / "branding" / "assets" / tail,
        root / "branding" / theme_assets.get("mark", ""),
    ]
    for p in candidates:
        if p and p.is_file():
            return p.resolve()
    return None


def parse_hex_color(color: str) -> tuple[float, float, float] | None:
    if not isinstance(color, str):
        return None
    color = color.strip()
    if not HEX_COLOR.match(color):
        return None
    h = color[1:]
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 8:
        h = h[:6]
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return r, g, b


def has_alpha_channel(color: str) -> bool:
    if not isinstance(color, str) or not color.startswith("#"):
        return False
    h = color[1:]
    return len(h) == 8


def relative_luminance(r: float, g: float, b: float) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = channel(r), channel(g), channel(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb1: tuple[float, float, float], rgb2: tuple[float, float, float]) -> float:
    l1 = relative_luminance(*rgb1)
    l2 = relative_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def resolve_role_color(theme: dict[str, Any], role_key: str) -> str | None:
    roles = theme.get("roles") or {}
    css_vars = theme.get("css_variables") or {}
    token_name = roles.get(role_key)
    if not token_name:
        return None
    var_key = f"--{token_name}" if not str(token_name).startswith("--") else str(token_name)
    if var_key in css_vars:
        return css_vars[var_key]
    if token_name in css_vars:
        return css_vars[token_name]
    return None


def validate_theme_tokens(result: BrandValidationResult, theme: dict[str, Any], limits: dict[str, Any]) -> None:
    if theme.get("_consumed_by_chatkit") is not False and "_consumed_by_chatkit" in theme:
        pass
    css_vars = theme.get("css_variables")
    roles = theme.get("roles")
    if not isinstance(css_vars, dict) or not css_vars:
        result.add("error", "theme_schema", "theme-tokens.json: css_variables must be a non-empty object")
        return
    if not isinstance(roles, dict) or not roles:
        result.add("error", "theme_schema", "theme-tokens.json: roles must be a non-empty object")
        return

    wcag = limits.get("wcag") or {}
    min_normal = float(wcag.get("normal_text_min_contrast", 4.5))

    pairs = [
        ("text on background", "text", "background", min_normal),
        ("text on surface", "text", "surface", min_normal),
        ("muted text on background", "muted_text", "background", min_normal),
        ("muted text on surface", "muted_text", "surface", min_normal),
    ]

    for label, fg_role, bg_role, threshold in pairs:
        fg_raw = resolve_role_color(theme, fg_role)
        bg_raw = resolve_role_color(theme, bg_role)
        if fg_raw is None or bg_raw is None:
            result.add("error", "theme_role", f"theme-tokens.json: missing role mapping for {fg_role} or {bg_role}")
            continue
        if has_alpha_channel(fg_raw) or has_alpha_channel(bg_raw):
            result.add(
                "error",
                "contrast_alpha",
                f"WCAG contrast check: alpha in {label} colors is unsupported; use opaque hex (#RRGGBB)",
            )
            continue
        fg = parse_hex_color(fg_raw)
        bg = parse_hex_color(bg_raw)
        if fg is None or bg is None:
            result.add("error", "theme_color", f"theme-tokens.json: unparseable color for {label}: {fg_raw!r} / {bg_raw!r}")
            continue
        ratio = contrast_ratio(fg, bg)
        if ratio < threshold:
            result.add(
                "error",
                "contrast_wcag_aa",
                f"WCAG AA (normal text, ≥{threshold}:1 assumed): {label} contrast {ratio:.2f}:1 below threshold "
                f"({fg_raw} on {bg_raw}). Token contrast only — not full UI WCAG compliance.",
            )


def _local_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def validate_svg_file(
    result: BrandValidationResult,
    path: Path,
    role: str,
    limits: dict[str, Any],
) -> None:
    if not path.is_file():
        result.add("error", "asset_missing", f"{role}: file not found: {path}")
        return
    size = path.stat().st_size
    size_limits = limits.get("asset_file_size_bytes") or {}
    max_bytes = int(size_limits.get(role, size_limits.get("mark", 2_097_152)))
    if size > max_bytes:
        result.add("error", "asset_size", f"{role}: {path.name} size {size} exceeds limit {max_bytes}")

    try:
        tree = ET.parse(path)
        root_el = tree.getroot()
    except ET.ParseError as e:
        result.add("error", "svg_invalid", f"{role}: invalid SVG XML in {path.name}: {e}")
        return

    for el in root_el.iter():
        tag = _local_tag(el.tag).lower()
        if tag in UNSAFE_SVG_TAGS:
            result.add("error", "svg_unsafe", f"{role}: disallowed SVG element <{tag}> in {path.name}")
        for attr_name, attr_val in el.attrib.items():
            local_attr = attr_name.split("}")[-1].lower()
            if local_attr.startswith(UNSAFE_SVG_ATTR_PREFIXES):
                result.add("error", "svg_unsafe", f"{role}: event handler {local_attr} in {path.name}")
            if local_attr in ("href", "xlink:href", "src") and isinstance(attr_val, str):
                if UNSAFE_HREF_SCHEMES.match(attr_val):
                    result.add("error", "svg_external", f"{role}: external/unsafe href in {path.name}: {attr_val[:80]}")

    dim_limits = limits.get("asset_dimension_px") or {}
    w_attr = root_el.get("width")
    h_attr = root_el.get("height")
    vb = root_el.get("viewBox")
    w, h = _svg_dimensions(w_attr, h_attr, vb)
    _check_svg_dims(result, role, w, h, dim_limits)


def _svg_dimensions(w_attr: str | None, h_attr: str | None, view_box: str | None) -> tuple[float | None, float | None]:
    def parse_len(s: str | None) -> float | None:
        if not s:
            return None
        m = re.match(r"^([\d.]+)", str(s).strip())
        return float(m.group(1)) if m else None

    w, h = parse_len(w_attr), parse_len(h_attr)
    if (w is None or h is None) and view_box:
        parts = view_box.split()
        if len(parts) == 4:
            try:
                w = w or float(parts[2])
                h = h or float(parts[3])
            except ValueError:
                pass
    return w, h


def _check_svg_dims(
    result: BrandValidationResult,
    role: str,
    w: float | None,
    h: float | None,
    dim_limits: dict[str, Any],
) -> None:
    if w is None or h is None:
        result.add("warn", "asset_dimensions", f"{role}: could not determine SVG dimensions (check viewBox)")
        return
    if role == "favicon":
        m = float(dim_limits.get("favicon_max", 512))
        if w > m or h > m:
            result.add("error", "asset_dimensions", f"favicon: {w}x{h} exceeds max {m}px")
    elif role == "mark":
        m = float(dim_limits.get("mark_max", 2048))
        if w > m or h > m:
            result.add("error", "asset_dimensions", f"mark: {w}x{h} exceeds max {m}px")
    elif role == "wordmark":
        mw = float(dim_limits.get("wordmark_max_width", 4096))
        mh = float(dim_limits.get("wordmark_max_height", 1024))
        if w > mw or h > mh:
            result.add("error", "asset_dimensions", f"wordmark: {w}x{h} exceeds max {mw}x{mh}px")
    elif role == "og":
        mw = float(dim_limits.get("og_max_width", 2400))
        mh = float(dim_limits.get("og_max_height", 1260))
        if w > mw or h > mh:
            result.add("error", "asset_dimensions", f"og: {w}x{h} exceeds max {mw}x{mh}px")


def validate_png_file(
    result: BrandValidationResult,
    path: Path,
    role: str,
    limits: dict[str, Any],
) -> None:
    if Image is None:
        result.add("warn", "png_optional", f"{role}: Pillow not installed; skipping PNG checks for {path.name}")
        return
    try:
        with Image.open(path) as im:
            im.verify()
    except Exception as e:
        result.add("error", "png_invalid", f"{role}: invalid PNG {path.name}: {e}")
        return
    with Image.open(path) as im:
        w, h = im.size
    dim_limits = limits.get("asset_dimension_px") or {}
    _check_svg_dims(result, role, float(w), float(h), dim_limits)


def validate_asset_path(
    result: BrandValidationResult,
    root: Path,
    rel_path: str,
    role: str,
) -> Path | None:
    if not rel_path or not isinstance(rel_path, str):
        result.add("error", "asset_path", f"{role}: missing asset path in theme-tokens.json")
        return None
    if rel_path.startswith(("http://", "https://", "//")):
        result.add("error", "asset_external", f"{role}: external asset reference not allowed: {rel_path}")
        return None
    if ".." in Path(rel_path).parts:
        result.add("error", "asset_traversal", f"{role}: path traversal rejected: {rel_path}")
        return None
    full = (root / "branding" / rel_path).resolve()
    branding_root = (root / "branding").resolve()
    try:
        full.relative_to(branding_root)
    except ValueError:
        result.add("error", "asset_traversal", f"{role}: path escapes branding/: {rel_path}")
        return None
    if not full.is_file():
        result.add("error", "asset_missing", f"{role}: referenced file missing: {rel_path}")
        return None
    if full.suffix.lower() == ".svg":
        limits = load_limits(root)
        validate_svg_file(result, full, role, limits)
    elif full.suffix.lower() == ".png":
        limits = load_limits(root)
        validate_png_file(result, full, role, limits)
    return full


def validate_persona_pack(result: BrandValidationResult, root: Path) -> None:
    path = root / "persona-templates.json"
    if not path.is_file():
        result.add("error", "persona_missing", "persona-templates.json not found")
        return
    try:
        pack = load_json(path)
    except json.JSONDecodeError as e:
        result.add("error", "persona_json", f"persona-templates.json: invalid JSON: {e}")
        return
    if pack.get("sync_mode") != "replace_platform":
        result.add("error", "persona_sync", "persona-templates.json: sync_mode must be replace_platform")
    templates = pack.get("templates") or []
    if not templates:
        result.add("error", "persona_empty", "persona-templates.json: templates must be non-empty")
    defaults = [t for t in templates if t.get("is_default")]
    if len(defaults) != 1:
        result.add("error", "persona_default", "persona-templates.json: exactly one is_default template required")


def validate_platform_settings(
    result: BrandValidationResult,
    root: Path,
    settings: dict[str, Any],
    limits: dict[str, Any],
) -> None:
    require_non_blank_localized(result, settings.get("product_name"), "product_name")
    for loc in REQUIRED_LOCALE_KEYS:
        pn = (settings.get("product_name") or {}).get(loc, "")
        if pn:
            check_length(result, str(pn), f"product_name.{loc}", int(limits["product_name_max_chars"]))
            check_no_html_injection(result, str(pn), f"product_name.{loc}")

    login_hero = settings.get("login_hero") or {}
    for part in ("title", "subtitle"):
        require_non_blank_localized(result, login_hero.get(part), f"login_hero.{part}")
        max_key = f"login_hero_{part}_max_chars"
        max_len = int(limits.get(max_key, limits["auth_subtitle_max_chars"]))
        for loc in REQUIRED_LOCALE_KEYS:
            val = (login_hero.get(part) or {}).get(loc, "")
            if val:
                check_length(result, str(val), f"login_hero.{part}.{loc}", max_len)
                check_no_html_injection(result, str(val), f"login_hero.{part}.{loc}")

    for block in ("auth_login", "auth_register"):
        auth = settings.get(block) or {}
        for part in ("title", "subtitle"):
            require_non_blank_localized(result, auth.get(part), f"{block}.{part}")
            max_len = int(
                limits["auth_title_max_chars"] if part == "title" else limits["auth_subtitle_max_chars"]
            )
            for loc in REQUIRED_LOCALE_KEYS:
                val = (auth.get(part) or {}).get(loc, "")
                if val:
                    check_length(result, str(val), f"{block}.{part}.{loc}", max_len)
                    check_no_html_injection(result, str(val), f"{block}.{part}.{loc}")

    require_non_blank_localized(result, settings.get("family_line"), "family_line")
    for loc in REQUIRED_LOCALE_KEYS:
        fl = (settings.get("family_line") or {}).get(loc, "")
        if fl:
            check_length(result, str(fl), f"family_line.{loc}", int(limits["family_line_max_chars"]))
            check_no_html_injection(result, str(fl), f"family_line.{loc}")

    logo_url = settings.get("logo_url")
    if not logo_url or not str(logo_url).strip():
        result.add("error", "logo_url_blank", "logo_url: required non-blank string")
    elif not is_safe_logo_path(str(logo_url)):
        result.add("error", "logo_url_unsafe", f"logo_url: must be site-root static path, no external URL: {logo_url!r}")

    doc_titles = settings.get("document_titles")
    if not isinstance(doc_titles, dict):
        result.add("error", "document_titles", "document_titles: required object")
    else:
        for key in ("admin", "web", "mobile"):
            if not str(doc_titles.get(key, "")).strip():
                result.add("error", "document_titles_blank", f"document_titles.{key}: required non-blank")


def run_validation(root: Path | None = None) -> BrandValidationResult:
    root = root or Path(__file__).resolve().parent.parent
    result = BrandValidationResult()
    limits = load_limits(root)

    ps_path = root / "branding" / "platform-settings.json"
    theme_path = root / "branding" / "theme-tokens.json"
    for p in (ps_path, theme_path):
        if not p.is_file():
            result.add("error", "missing_file", f"Missing required file: {p.relative_to(root)}")
            return result

    try:
        settings = load_json(ps_path)
    except json.JSONDecodeError as e:
        result.add("error", "json_invalid", f"platform-settings.json: {e}")
        settings = {}

    try:
        theme = load_json(theme_path)
    except json.JSONDecodeError as e:
        result.add("error", "json_invalid", f"theme-tokens.json: {e}")
        theme = {}

    validate_platform_settings(result, root, settings, limits)
    validate_theme_tokens(result, theme, limits)

    assets = theme.get("assets") or {}
    for role in ("favicon", "mark", "wordmark", "og"):
        validate_asset_path(result, root, assets.get(role, ""), role)

    if settings.get("logo_url"):
        logo_file = resolve_logo_file(root, str(settings["logo_url"]), assets)
        if logo_file is None:
            result.add("error", "logo_missing", f"logo_url does not resolve to a local file under branding/assets: {settings['logo_url']}")

    validate_persona_pack(result, root)
    return result


def print_result(result: BrandValidationResult) -> int:
    for issue in result.issues:
        prefix = "ERROR" if issue.level == "error" else "WARN"
        print(f"{prefix} [{issue.code}]: {issue.message}", file=sys.stderr if issue.level == "error" else sys.stdout)
    if result.ok:
        print("validate-branding: PASS")
        return 0
    print("validate-branding: FAIL", file=sys.stderr)
    return 1
