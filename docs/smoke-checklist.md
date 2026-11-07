[English](./smoke-checklist.md) | [简体中文](./smoke-checklist.zh-CN.md) | [繁體中文](./smoke-checklist.zh-TW.md)

# Smoke checklist

Run after Phase 1 (default stack) and Phase 2 (white-label overlays) from [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md).

## Infrastructure

- [ ] Release unpacked and compose or Helm deploy reports healthy services (`docker compose ps` or equivalent).
- [ ] Login / app URL responds (your configured host, e.g. `https://hub.example.com`).

## Branding (Option B)

- [ ] Splash and login show **your** `product_name` from `branding/platform-settings.json` (not upstream default product strings).
- [ ] Logo resolves: `logo_url` loads (static mount or upload path).
- [ ] `auth_login` / `auth_register` titles match your seed copy.
- [ ] Admin can **GET** platform settings matching your seed (fields your release supports).

## Persona pack

- [ ] `PERSONA_TEMPLATE_CONFIG_PATH` points at your mounted `persona-templates.json`.
- [ ] One-shot sync with `replace_platform` completed (dry-run first, then apply).
- [ ] Persona picker lists **only** templates from your pack (no full default catalog clutter).
- [ ] Default role matches the template with `is_default: true` in your JSON (e.g. **General**).

## Validation before deploy

- [ ] `./scripts/validate-artifacts.sh` exits 0 on the fork.

## OAuth (only if Phase 1.5 ran)

- [ ] `OAUTH_PROVIDER_ENABLED=true` and issuer URLs match your host.
- [ ] OAuth authorize endpoint does not return "provider disabled" 404.

## Cold-path bar (product)

A new customer or agent should reach branded login chrome and a pruned persona pack **without editing chatkit source**, given: release URL, this repo path, and credentials they supply.
