# Customize your white-label FinHub

All customer-facing changes for a typical v1 deploy live **in this repository** — no chatkit-web or chatkit-middleware forks required.

## 1. Product name and auth chrome

Edit [`branding/platform-settings.json`](../branding/platform-settings.json):

- `product_name` — shown on splash, login, and masthead
- `login_hero`, `auth_login`, `auth_register` — headlines and subtitles (zh/en)
- `family_line` — auth footer line
- `logo_url` — path after static mount (default `/static/branding/acme-mark.svg`)
- `document_titles` — browser tab titles

Run `./scripts/validate-artifacts.sh` after edits.

## 2. Logos and static brand

Replace files under [`branding/assets/`](../branding/assets/):

- `acme-mark.svg` — square mark (rename files if you prefer; update `logo_url` accordingly)
- `acme-wordmark.svg`, `favicon.svg`, `og-acme.svg`

Optional: skip static files and upload via admin **`PUT /admin/config/platform-settings/logo`**, then point `logo_url` at `/platform-uploads/...`.

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
