[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# 品牌製品

客戶擁有的文案與 FinHub 認證介面（Option B）的靜態品牌資源。

## 檔案

| File | Purpose |
|------|---------|
| [`platform-settings.json`](./platform-settings.json) | Option B seed: product name, login/register hero, `logo_url`, `document_titles` |
| [`theme-tokens.json`](./theme-tokens.json) | Design reference only (`_consumed_by_chatkit: false`) |
| [`assets/`](./assets/) | Mark, wordmark, favicon, OG placeholders |

## 套用平台設定

堆疊健康且您的發佈套件包含 Option B platform-settings 支援後：

```bash
export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
  -H "Content-Type: application/json" \
  -d @branding/platform-settings.json
```

將 `branding/assets/` 掛載到 `/static/branding`（見 `deploy/compose/` 或 `deploy/helm/`），以便 `logo_url` 可解析。透過 `GET /platform/settings` 以及登入 / 啟動介面驗證。

## 種子中的欄位

| Key | Role |
|-----|------|
| `product_name` | Masthead / splash |
| `login_hero` | Auth left-pane headline |
| `auth_login` / `auth_register` | Form titles and leads |
| `family_line` | Footer / family line on auth |
| `auth_show_marquee` | Marquee toggle (`false` in template) |
| `logo_url` | Static mark path after asset mount |
| `document_titles` | Browser titles (admin / web / mobile) |
