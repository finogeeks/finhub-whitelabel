[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Branding artifacts

Customer-owned copy and static brand for FinHub auth chrome (Option B).

## Files

| File | Purpose |
|------|---------|
| [`platform-settings.json`](./platform-settings.json) | Option B seed: product name, login/register hero, `logo_url`, `document_titles` |
| [`theme-tokens.json`](./theme-tokens.json) | Design reference only (`_consumed_by_chatkit: false`) |
| [`assets/`](./assets/) | Mark, wordmark, favicon, OG placeholders |

## Apply platform settings

After the stack is healthy and your release includes Option B platform-settings support:

```bash
export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
  -H "Content-Type: application/json" \
  -d @branding/platform-settings.json
```

Mount `branding/assets/` at `/static/branding` (see `deploy/compose/` or `deploy/helm/`) so `logo_url` resolves. Verify with `GET /platform/settings` and the login / splash UI.

## Fields in the seed

| Key | Role |
|-----|------|
| `product_name` | Masthead / splash |
| `login_hero` | Auth left-pane headline |
| `auth_login` / `auth_register` | Form titles and leads |
| `family_line` | Footer / family line on auth |
| `auth_show_marquee` | Marquee toggle (`false` in template) |
| `logo_url` | Static mark path after asset mount |
| `document_titles` | Browser titles (admin / web / mobile) |
