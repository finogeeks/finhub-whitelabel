---
name: finhub-brand
description: >-
  Use when validating or previewing FinHub white-label branding before deploy:
  run scripts against branding/platform-settings.json, branding/theme-tokens.json,
  and branding/assets/, generate the static approximate login preview, and compare
  screenshots with the live login after deploy. Customer repo skill only.
---
# FinHub white-label brand preview and validation

Validate branding artifacts and produce a **static, inert** login preview from this repository. The preview is an **approximation** — always compare against the deployed login screen after Phase 2.

No chatkit-web / AuthShell code is copied. Preview uses a small standalone HTML renderer in `scripts/preview_login_lib.py`.

## When to use

- After editing `branding/platform-settings.json`, `branding/theme-tokens.json`, or `branding/assets/`
- Before opening a deploy PR or handing off to `skills/finhub-deploy`
- After deploy, to compare local preview PNGs with a real login screenshot (see `docs/smoke-checklist.md`)

## Quick commands (no network for validate/preview render)

From the repo root:

```bash
# Full artifact gate (presence + JSON + branding rules)
./scripts/validate-artifacts.sh

# Branding-only validator
python3 scripts/validate-branding.py

# Static HTML preview (English copy)
python3 scripts/preview-login.py

# Desktop + mobile PNG screenshots (needs Playwright once)
pip install -r scripts/requirements-dev.txt
python -m playwright install chromium
python3 scripts/capture-preview-screenshots.py
```

Outputs:

| Artifact | Path |
|----------|------|
| Preview HTML | `artifacts/brand-preview/login-preview-en.html` |
| Desktop PNG | `artifacts/brand-preview/login-preview-desktop.png` |
| Mobile PNG | `artifacts/brand-preview/login-preview-mobile.png` |

Open the HTML via `file://` locally. The yellow banner reads: **Approximate brand preview — compare with deployed login screen**.

## What validation checks

Documented limits live in [`scripts/brand_validation_limits.json`](../scripts/brand_validation_limits.json) — adjust for your fork, then re-run validation.

- **Schema & copy (EN required in v1):** non-blank `product_name`, `login_hero`, `auth_login`, `auth_register`, `family_line`, `document_titles`, `logo_url`
- **Length limits:** product name, auth titles/subtitles, hero title/subtitle, family line (per limits file — not silent runtime caps)
- **Assets:** `theme-tokens.json` `assets` roles (`favicon`, `mark`, `wordmark`, `og`) resolve under `branding/`; no traversal or external URLs
- **Images:** SVG well-formed; reject `<script>`, event handlers, external `javascript:`/`http(s):` refs; PNG validated when present; size/dimension ceilings per role
- **Logo path:** `logo_url` is a safe root-relative static path; file exists under `branding/assets`
- **Theme:** unknown or missing `roles` / `css_variables` keys fail with actionable errors (no silent defaults)
- **Contrast:** WCAG **AA for normal text (4.5:1)** on documented token pairs (text/muted on background/surface). Opaque `#RRGGBB` only; alpha hex unsupported. **Token contrast ≠ full product WCAG sign-off.**
- **Injection:** branding strings must not contain script/form markup patterns; preview HTML escapes all copy
- **Persona pack:** `sync_mode: replace_platform`, non-empty templates, exactly one `is_default: true`

## Fidelity and licensing

- Preview layout is **inspired by** auth chrome fields in `platform-settings.json`, not pixel-matched to production AuthShell.
- Deployed login UI and upstream CSS remain authoritative for production QA.
- Placeholder brand **Acme Hub** stays in the template; replace before production.

## Post-deploy comparison

After Phase 2 from [`finhub-deploy`](../finhub-deploy/SKILL.md):

1. Capture a screenshot of the real login URL (desktop and mobile).
2. Side-by-side with `artifacts/brand-preview/login-preview-*.png`.
3. Confirm product name, logo, hero, form titles, and theme colors are in the same ballpark; note intentional upstream differences.

See [`docs/smoke-checklist.md`](../../docs/smoke-checklist.md) — **Brand preview vs live login** section.

## Optional dev dependencies

`scripts/requirements-dev.txt` — Pillow (PNG), pytest, Playwright (screenshots). Validation and HTML generation use the Python standard library except Pillow for optional PNG assets.

## Hard rules

- Do not enable real auth inputs or network calls in the preview generator
- Do not call deployed admin APIs from these scripts
- Do not copy proprietary AuthShell source from chatkit repos into this template
- Default deploy path (`finhub-deploy` Phase 1 → 2) unchanged; OAuth still opt-in
