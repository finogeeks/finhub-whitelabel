[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# 品牌资源

将这些占位 SVG 替换为您的标记、字标、favicon 和 Open Graph 图片。

| File | Typical use |
|------|-------------|
| `acme-mark.svg` | Square mark; referenced by `logo_url` in `platform-settings.json` |
| `acme-wordmark.svg` | Horizontal wordmark |
| `favicon.svg` | Browser tab icon |
| `og-acme.svg` | Social / link preview (export to PNG if your edge requires raster) |

Compose 与 Helm 覆盖层将此目录挂载到 **`/static/branding`**，以便类似 `/static/branding/acme-mark.svg` 的路径可公开访问。

也可通过管理员 **`PUT /admin/config/platform-settings/logo`** 上传 logo，并在 `logo_url` 中使用 `/platform-uploads/...`。
