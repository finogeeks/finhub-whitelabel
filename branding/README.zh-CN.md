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

线上 PUT 只保存 `product_name` 和 `login_hero`，不会采用本文件里的 `logo_url`。种子之后请在**管理端 → 平台设置**上传标。见 [`docs/admin-and-whitelabel.zh-CN.md`](../docs/admin-and-whitelabel.zh-CN.md)。通过 `GET /platform/settings` 以及登录 / 启动界面验证。

## 种子中的字段

| 字段 | 作用 | 线上 PUT |
| --- | --- | --- |
| `product_name` | 启动页 / 顶栏 | 会保存 |
| `login_hero` | 登录页主标题与副标题 | 会保存 |
| `auth_login` / `auth_register` | 预览用的表单标题 | 丢掉 |
| `family_line` | 预览用的页脚 | 丢掉 |
| `auth_show_marquee` | 预览用的滚动开关 | 丢掉 |
| `logo_url` | 预览资源路径 | 丢掉；登录标靠管理端上传 |
| `document_titles` | 预览用的浏览器标题 | 丢掉；由中文产品名派生 |
