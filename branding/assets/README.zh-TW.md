[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# 品牌資源

將這些佔位 SVG 替換為您的標記、字標、favicon 和 Open Graph 圖片。

| File | Typical use |
|------|-------------|
| `acme-mark.svg` | Square mark; referenced by `logo_url` in `platform-settings.json` |
| `acme-wordmark.svg` | Horizontal wordmark |
| `favicon.svg` | Browser tab icon |
| `og-acme.svg` | Social / link preview (export to PNG if your edge requires raster) |

這些檔案供本機品牌預覽。執行中的登入標是管理端上傳的檔案（`POST /admin/config/platform-settings/logo` → `/platform-uploads/...`），不是種子裡的 `logo_url`。見 [`docs/admin-and-whitelabel.zh-TW.md`](../../docs/admin-and-whitelabel.zh-TW.md)。
