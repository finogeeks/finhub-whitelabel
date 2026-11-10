[English](./customize.md) | [简体中文](./customize.zh-CN.md) | [繁體中文](./customize.zh-TW.md)

# Customize your white-label FinHub

All customer-facing **seed** changes for a typical v1 deploy live **in this repository** — no chatkit-web or chatkit-middleware forks required. After the stack is up, day-2 logo, wording, and preset skills are changed in the FinHub admin console. Boundaries: [`admin-and-whitelabel.md`](./admin-and-whitelabel.md).

## 1. Product name and login hero

Edit [`branding/platform-settings.json`](../branding/platform-settings.json):

- `product_name`, `login_hero` — the only fields the live settings PUT stores. A later seed PUT overwrites the same fields saved in **Admin → Platform settings**.
- `auth_login`, `auth_register`, `family_line`, `auth_show_marquee`, `document_titles`, `logo_url` — kept for this repo's validator and static preview. The live PUT drops them. Browser titles follow the Chinese product name.

Run `./scripts/validate-artifacts.sh` after edits.

## 2. Logos and static brand

Replace files under [`branding/assets/`](../branding/assets/) for the local preview (mark, wordmark, favicon, OG).

The running login mark is the file uploaded in **Admin → Platform settings** (`/platform-uploads/...`). Mounting `branding/assets/` does not set `logo_url`. Re-running the seed PUT does not clear an uploaded logo.

## 3. Persona starter pack

Edit [`persona-templates.json`](../persona-templates.json):

- Keep `"sync_mode": "replace_platform"` for one-shot prune
- Set exactly one template with `"is_default": true`
- Use `template_format`: `soul_identity` with `soul_template` and `identity_template`
- `avatar_url` may be empty or point at your hosted avatars

See [`persona-pack-pin.md`](./persona-pack-pin.md) for pin + sync steps.

## 4. Host, TLS, and ingress

- **Compose** — set public URL in your release `.env` and reverse proxy; use `ADMIN_BASE` when seeding platform settings (see `deploy/compose/README.md`).
- **Helm** — override `ingress.hosts` in `deploy/helm/values-whitelabel.yaml` (default example: `hub.example.com`).

Do not hardcode vendor reference hostnames as **required** defaults in your fork unless that is your real production host.

## 5. Theme tokens (optional)

[`branding/theme-tokens.json`](../branding/theme-tokens.json) is a **design SoT** for your team (`_consumed_by_chatkit: false`). Upstream may not apply these keys until platform theme support exists.

## 6. OAuth (opt-in)

Only if you need Identity as an OAuth provider for embed or third-party RPs:

- Copy [`deploy/oauth-provider.env.example`](../deploy/oauth-provider.env.example) into your release env
- Follow **Phase 1.5** in [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md)

Default FinHub white-label path does **not** require OAuth.

## 7. Deploy

Give your agent:

- Offline release tarball URL
- Path to this fork
- Admin credentials for platform-settings PUT

Load [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md).

## Optional later

- Knowledge / resource seeds under `data/` (not in v1 template)
- Full CSS theme consumption from `theme-tokens.json`
- Additional persona roles — keep slugs unique and re-run sync after changes
