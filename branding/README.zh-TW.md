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

線上 PUT 只儲存 `product_name` 和 `login_hero`，不會採用本檔案裡的 `logo_url`。種子之後請在**管理端 → 平台設定**上傳標。見 [`docs/admin-and-whitelabel.zh-TW.md`](../docs/admin-and-whitelabel.zh-TW.md)。透過 `GET /platform/settings` 以及登入 / 啟動介面驗證。

## 種子中的欄位

| 欄位 | 作用 | 線上 PUT |
| --- | --- | --- |
| `product_name` | 啟動頁 / 頂欄 | 會儲存 |
| `login_hero` | 登入頁主標題與副標題 | 會儲存 |
| `auth_login` / `auth_register` | 預覽用的表單標題 | 丟掉 |
| `family_line` | 預覽用的頁尾 | 丟掉 |
| `auth_show_marquee` | 預覽用的捲動開關 | 丟掉 |
| `logo_url` | 預覽資源路徑 | 丟掉；登入標靠管理端上傳 |
| `document_titles` | 預覽用的瀏覽器標題 | 丟掉；由中文產品名衍生 |
