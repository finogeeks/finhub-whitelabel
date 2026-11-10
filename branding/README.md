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

The live PUT stores `product_name` and `login_hero` only. It does not apply `logo_url` from this file. Upload the mark in **Admin → Platform settings** after the seed. See [`docs/admin-and-whitelabel.md`](../docs/admin-and-whitelabel.md). Verify with `GET /platform/settings` and the login / splash UI.

## Fields in the seed

| Key | Role | Live PUT |
|-----|------|----------|
| `product_name` | Masthead / splash | Stored |
| `login_hero` | Auth left-pane headline | Stored |
| `auth_login` / `auth_register` | Preview form titles | Dropped |
| `family_line` | Preview footer line | Dropped |
| `auth_show_marquee` | Preview marquee toggle | Dropped |
| `logo_url` | Preview asset path | Dropped; admin upload sets the live mark |
| `document_titles` | Preview browser titles | Dropped; derived from the Chinese product name |
