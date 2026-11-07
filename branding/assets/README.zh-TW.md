[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# 品牌資源

將這些佔位 SVG 替換為您的標記、字標、favicon 和 Open Graph 圖片。

| File | Typical use |
|------|-------------|
| `acme-mark.svg` | Square mark; referenced by `logo_url` in `platform-settings.json` |
| `acme-wordmark.svg` | Horizontal wordmark |
| `favicon.svg` | Browser tab icon |
| `og-acme.svg` | Social / link preview (export to PNG if your edge requires raster) |

Compose 與 Helm 覆寫層將此目錄掛載到 **`/static/branding`**，以便類似 `/static/branding/acme-mark.svg` 的路徑可公開存取。

亦可透過管理員 **`PUT /admin/config/platform-settings/logo`** 上傳 logo，並在 `logo_url` 中使用 `/platform-uploads/...`。
