[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Brand assets

Replace these placeholder SVGs with your mark, wordmark, favicon, and Open Graph image.

| File | Typical use |
|------|-------------|
| `acme-mark.svg` | Square mark; referenced by `logo_url` in `platform-settings.json` |
| `acme-wordmark.svg` | Horizontal wordmark |
| `favicon.svg` | Browser tab icon |
| `og-acme.svg` | Social / link preview (export to PNG if your edge requires raster) |

Compose and Helm overlays mount this directory at **`/static/branding`** so paths like `/static/branding/acme-mark.svg` resolve publicly.

Alternatively upload a logo via admin **`PUT /admin/config/platform-settings/logo`** and use `/platform-uploads/...` in `logo_url`.
