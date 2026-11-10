[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Brand assets

Replace these placeholder SVGs with your mark, wordmark, favicon, and Open Graph image.

| File | Typical use |
|------|-------------|
| `acme-mark.svg` | Square mark; referenced by `logo_url` in `platform-settings.json` |
| `acme-wordmark.svg` | Horizontal wordmark |
| `favicon.svg` | Browser tab icon |
| `og-acme.svg` | Social / link preview (export to PNG if your edge requires raster) |

These files feed the local brand preview. The live login mark is the admin upload (`POST /admin/config/platform-settings/logo` → `/platform-uploads/...`), not `logo_url` in the seed. See [`docs/admin-and-whitelabel.md`](../../docs/admin-and-whitelabel.md).
