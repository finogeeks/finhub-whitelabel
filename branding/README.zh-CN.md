[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# 品牌制品

客户拥有的文案与 FinHub 认证界面（Option B）的静态品牌资源。

## 文件

| File | Purpose |
|------|---------|
| [`platform-settings.json`](./platform-settings.json) | Option B seed: product name, login/register hero, `logo_url`, `document_titles` |
| [`theme-tokens.json`](./theme-tokens.json) | Design reference only (`_consumed_by_chatkit: false`) |
| [`assets/`](./assets/) | Mark, wordmark, favicon, OG placeholders |

## 应用平台设置

堆栈健康且您的发布包包含 Option B platform-settings 支持后：

```bash
export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
  -H "Content-Type: application/json" \
  -d @branding/platform-settings.json
```

将 `branding/assets/` 挂载到 `/static/branding`（见 `deploy/compose/` 或 `deploy/helm/`），以便 `logo_url` 可解析。通过 `GET /platform/settings` 以及登录 / 启动界面验证。

## 种子中的字段

| Key | Role |
|-----|------|
| `product_name` | Masthead / splash |
| `login_hero` | Auth left-pane headline |
| `auth_login` / `auth_register` | Form titles and leads |
| `family_line` | Footer / family line on auth |
| `auth_show_marquee` | Marquee toggle (`false` in template) |
| `logo_url` | Static mark path after asset mount |
| `document_titles` | Browser titles (admin / web / mobile) |
