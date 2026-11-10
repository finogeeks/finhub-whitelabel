[English](./smoke-checklist.md) | [简体中文](./smoke-checklist.zh-CN.md) | [繁體中文](./smoke-checklist.zh-TW.md)

# Smoke checklist

Run after Phase 1 (default stack) and Phase 2 (white-label overlays) from [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md).

## Infrastructure

- [ ] Release unpacked and compose or Helm deploy reports healthy services (`docker compose ps` or equivalent).
- [ ] Login / app URL responds (your configured host, e.g. `https://hub.example.com`).

## Core product (Phase 1)

- [ ] Sign in with bootstrap or configured admin credentials.
- [ ] Send a chat message and receive a **streamed** assistant reply (tokens/chunks arrive over time — not only a single blocking response).

## Branding (Option B)

- [ ] Splash and login show **your** `product_name` and `login_hero` from `branding/platform-settings.json` (not upstream default product strings).
- [ ] Login mark is the file uploaded in **Admin → Platform settings**. The seed `logo_url` alone does not set it. See [`admin-and-whitelabel.md`](./admin-and-whitelabel.md).
- [ ] `GET /platform/settings` matches the seed for `product_name` and `login_hero`. Browser titles follow the Chinese product name. `auth_login` / `auth_register` are preview-only.

## Persona pack

- [ ] `PERSONA_TEMPLATE_CONFIG_PATH` points at your mounted `persona-templates.json`.
- [ ] One-shot sync with `replace_platform` completed (dry-run first, then apply).
- [ ] Persona picker lists **only** templates from your pack (no full default catalog clutter).
- [ ] Default role matches the template with `is_default: true` in your JSON (e.g. **General**).

## Validation before deploy

- [ ] `./scripts/validate-artifacts.sh` exits 0 on the fork.
- [ ] Optional: `python3 scripts/preview-login.py` and review `artifacts/brand-preview/login-preview-en.html`.

## Brand preview vs live login (after Phase 2)

- [ ] Generate local reference PNGs: `python3 scripts/capture-preview-screenshots.py` (see [`scripts/README.md`](../scripts/README.md)).
- [ ] Capture **deployed** login screenshots (desktop + mobile) at your public URL.
- [ ] Compare product name, logo/mark, login hero copy, auth titles, and theme colors against `artifacts/brand-preview/login-preview-*.png`.
- [ ] Treat differences in layout, fonts, or optional chrome as expected unless branding seed or assets are wrong — preview is labelled **approximate** ([`docs/brand-preview.md`](./brand-preview.md)).

## OAuth (only if Phase 1.5 ran)

- [ ] `OAUTH_PROVIDER_ENABLED=true` and issuer URLs match your host.
- [ ] OAuth authorize endpoint does not return "provider disabled" 404.

## Cold-path bar (product)

A new customer or agent should reach branded login chrome and a pruned persona pack **without editing chatkit source**, given: release URL, this repo path, and credentials they supply.
