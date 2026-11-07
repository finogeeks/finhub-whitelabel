"""Static inert login preview renderer (no AuthShell, no network at render time)."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


APPROXIMATION_BANNER = (
    "Approximate brand preview — compare with deployed login screen"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pick_locale(obj: dict[str, Any] | None, locale: str = "en") -> str:
    if not isinstance(obj, dict):
        return ""
    return str(obj.get(locale) or obj.get("en") or next(iter(obj.values()), ""))


def resolve_css_var(theme: dict[str, Any], role_key: str, fallback: str = "#000") -> str:
    roles = theme.get("roles") or {}
    css_vars = theme.get("css_variables") or {}
    token = roles.get(role_key)
    if not token:
        return fallback
    key = f"--{token}" if not str(token).startswith("--") else str(token)
    return str(css_vars.get(key) or css_vars.get(token) or fallback)


def logo_src_for_html(root: Path, logo_url: str, theme: dict[str, Any]) -> str:
    """Return a relative path from preview HTML dir to the logo file."""
    assets = theme.get("assets") or {}
    tail = Path(logo_url).name if logo_url else ""
    logo_path = root / "branding" / "assets" / tail
    if not logo_path.is_file():
        mark = assets.get("mark", "assets/acme-mark.svg")
        logo_path = root / "branding" / mark
    rel = Path("../../branding") / logo_path.relative_to(root / "branding")
    return html.escape(str(rel).replace("\\", "/"), quote=True)


def build_preview_html(root: Path, locale: str = "en") -> str:
    settings = load_json(root / "branding" / "platform-settings.json")
    theme = load_json(root / "branding" / "theme-tokens.json")

    product = html.escape(pick_locale(settings.get("product_name"), locale))
    hero_title = html.escape(pick_locale((settings.get("login_hero") or {}).get("title"), locale))
    hero_sub = html.escape(pick_locale((settings.get("login_hero") or {}).get("subtitle"), locale))
    login_title = html.escape(pick_locale((settings.get("auth_login") or {}).get("title"), locale))
    login_sub = html.escape(pick_locale((settings.get("auth_login") or {}).get("subtitle"), locale))
    family = html.escape(pick_locale(settings.get("family_line"), locale))
    doc_title = html.escape(
        str((settings.get("document_titles") or {}).get("web") or product)
    )

    paper = html.escape(resolve_css_var(theme, "background", "#f8fafc"))
    ink = html.escape(resolve_css_var(theme, "text", "#0f172a"))
    panel = html.escape(resolve_css_var(theme, "surface", "#ffffff"))
    accent = html.escape(resolve_css_var(theme, "accent", "#2563eb"))
    accent_hover = html.escape(resolve_css_var(theme, "accent_hover", "#1d4ed8"))
    muted = html.escape(resolve_css_var(theme, "muted_text", "#64748b"))
    rule = html.escape(resolve_css_var(theme, "border", "#cbd5e1"))

    sans = html.escape((theme.get("typography") or {}).get("sans", "system-ui, sans-serif"))
    logo_src = logo_src_for_html(root, str(settings.get("logo_url", "")), theme)
    banner = html.escape(APPROXIMATION_BANNER)

    favicon_rel = "../../branding/assets/favicon.svg"
    assets = theme.get("assets") or {}
    if assets.get("favicon"):
        favicon_rel = "../../branding/" + str(assets["favicon"]).replace("\\", "/")

    return f"""<!DOCTYPE html>
<html lang="{html.escape(locale)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>{doc_title} — brand preview</title>
  <link rel="icon" href="{html.escape(favicon_rel)}" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: {sans};
      background: {paper};
      color: {ink};
      min-height: 100vh;
    }}
    .approx-banner {{
      background: #fef3c7;
      color: #92400e;
      border-bottom: 1px solid #f59e0b;
      padding: 0.65rem 1rem;
      font-size: 0.875rem;
      text-align: center;
      font-weight: 600;
    }}
    .shell {{
      display: flex;
      flex-wrap: wrap;
      min-height: calc(100vh - 42px);
    }}
    .hero {{
      flex: 1 1 320px;
      padding: 2.5rem 2rem;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 1rem;
      max-width: 560px;
    }}
    .hero h1 {{
      font-size: clamp(1.75rem, 4vw, 2.25rem);
      font-weight: 700;
      margin: 0;
      line-height: 1.2;
    }}
    .hero p {{
      margin: 0;
      color: {muted};
      font-size: 1.05rem;
      line-height: 1.5;
    }}
    .auth {{
      flex: 1 1 360px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }}
    .card {{
      width: 100%;
      max-width: 420px;
      background: {panel};
      border: 1px solid {rule};
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }}
    .brand-row {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
    }}
    .brand-row img {{
      width: 40px;
      height: 40px;
      border-radius: 8px;
    }}
    .brand-row span {{
      font-weight: 600;
      font-size: 1.1rem;
    }}
    .card h2 {{
      margin: 0 0 0.35rem;
      font-size: 1.35rem;
    }}
    .card .lead {{
      margin: 0 0 1.5rem;
      color: {muted};
      font-size: 0.95rem;
    }}
    .field {{
      margin-bottom: 1rem;
    }}
    .field label {{
      display: block;
      font-size: 0.8rem;
      font-weight: 600;
      margin-bottom: 0.35rem;
    }}
    .fake-input {{
      height: 42px;
      border: 1px solid {rule};
      border-radius: 8px;
      background: #f1f5f9;
      display: flex;
      align-items: center;
      padding: 0 0.75rem;
      color: {muted};
      font-size: 0.9rem;
      user-select: none;
      pointer-events: none;
    }}
    .fake-btn {{
      width: 100%;
      height: 44px;
      border: none;
      border-radius: 8px;
      background: {accent};
      color: #fff;
      font-weight: 600;
      font-size: 0.95rem;
      margin-top: 0.5rem;
      opacity: 0.85;
      pointer-events: none;
      user-select: none;
    }}
    .family {{
      margin-top: 1.25rem;
      text-align: center;
      font-size: 0.8rem;
      color: {muted};
    }}
    .note {{
      margin-top: 1rem;
      font-size: 0.75rem;
      color: {muted};
      line-height: 1.4;
    }}
  </style>
</head>
<body>
  <div class="approx-banner" role="note">{banner}</div>
  <div class="shell">
    <section class="hero" aria-label="Login hero">
      <h1>{hero_title}</h1>
      <p>{hero_sub}</p>
    </section>
    <section class="auth" aria-label="Sign-in preview (non-functional)">
      <div class="card">
        <div class="brand-row">
          <img src="{logo_src}" alt="" width="40" height="40" />
          <span>{product}</span>
        </div>
        <h2>{login_title}</h2>
        <p class="lead">{login_sub}</p>
        <div class="field">
          <label>Email (preview placeholder)</label>
          <div class="fake-input" aria-hidden="true">you@example.com</div>
        </div>
        <div class="field">
          <label>Password (preview placeholder)</label>
          <div class="fake-input" aria-hidden="true">••••••••</div>
        </div>
        <button type="button" class="fake-btn" disabled aria-disabled="true">Sign in (preview only)</button>
        <p class="family">{family}</p>
        <p class="note">Non-interactive preview. No credentials are collected. Theme from branding/theme-tokens.json; copy from branding/platform-settings.json.</p>
      </div>
    </section>
  </div>
</body>
</html>
"""


def write_preview(root: Path, locale: str = "en") -> Path:
    out_dir = root / "artifacts" / "brand-preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "login-preview-en.html"
    out_path.write_text(build_preview_html(root, locale), encoding="utf-8")
    return out_path
