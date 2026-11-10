[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# 品牌资源

将这些占位 SVG 替换为您的标记、字标、favicon 和 Open Graph 图片。

| File | Typical use |
|------|-------------|
| `acme-mark.svg` | Square mark; referenced by `logo_url` in `platform-settings.json` |
| `acme-wordmark.svg` | Horizontal wordmark |
| `favicon.svg` | Browser tab icon |
| `og-acme.svg` | Social / link preview (export to PNG if your edge requires raster) |

这些文件供本地品牌预览。运行中的登录标是管理端上传的文件（`POST /admin/config/platform-settings/logo` → `/platform-uploads/...`），不是种子里的 `logo_url`。见 [`docs/admin-and-whitelabel.zh-CN.md`](../../docs/admin-and-whitelabel.zh-CN.md)。
