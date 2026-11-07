[English](./customize.md) | [简体中文](./customize.zh-CN.md) | [繁體中文](./customize.zh-TW.md)

# 定制白标 FinHub

典型 v1 部署中所有面向客户的变更均在**本仓库**完成 — 无需 fork chatkit-web 或 chatkit-middleware。

## 1. 产品名称与认证界面

编辑 [`branding/platform-settings.json`](../branding/platform-settings.json)：

- `product_name` — 显示于启动页、登录页与顶栏
- `login_hero`, `auth_login`, `auth_register` — 标题与副标题（zh/en）
- `family_line` — 认证页页脚行
- `logo_url` — 静态挂载后的路径（默认 `/static/branding/acme-mark.svg`）
- `document_titles` — 浏览器标签标题

编辑后运行 `./scripts/validate-artifacts.sh`。

## 2. Logo 与静态品牌

替换 [`branding/assets/`](../branding/assets/) 下的文件：

- `acme-mark.svg` — 方形标记（可按需重命名文件；同步更新 `logo_url`）
- `acme-wordmark.svg`, `favicon.svg`, `og-acme.svg`

可选：跳过静态文件，通过管理员 **`PUT /admin/config/platform-settings/logo`** 上传，然后将 `logo_url` 指向 `/platform-uploads/...`。

## 3. 人设入门包

编辑 [`persona-templates.json`](../persona-templates.json)：

- 一次性修剪请保持 `"sync_mode": "replace_platform"`
- 恰好一个模板设置 `"is_default": true`
- 使用 `template_format`：`soul_identity`，含 `soul_template` 与 `identity_template`
- `avatar_url` 可为空或指向您托管的头像

固定与同步步骤见 [`persona-pack-pin.md`](./persona-pack-pin.md)。

## 4. 主机、TLS 与 ingress

- **Compose** — 在发布 `.env` 与反向代理中设置公开 URL；种子化 platform settings 时使用 `ADMIN_BASE`（见 `deploy/compose/README.md`）。
- **Helm** — 在 `deploy/helm/values-whitelabel.yaml` 中覆盖 `ingress.hosts`（默认示例：`hub.example.com`）。

除非那就是您的真实生产主机，否则不要在 fork 中将厂商参考主机名硬编码为**必需**默认值。

## 5. 主题令牌（可选）

[`branding/theme-tokens.json`](../branding/theme-tokens.json) 是团队用的**设计 SoT**（`_consumed_by_chatkit: false`）。在上游平台主题支持出现之前，这些键可能不会被应用。

## 6. OAuth（可选）

仅在需要将 Identity 作为 OAuth 提供方用于 embed 或第三方 RP 时：

- 将 [`deploy/oauth-provider.env.example`](../deploy/oauth-provider.env.example) 复制到发布环境
- 遵循 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) 中的 **Phase 1.5**

默认 FinHub 白标路径**不**需要 OAuth。

## 7. 部署

向您的 **AI 代理** 提供：

- 离线发布 tarball URL
- 本 fork 路径
- 用于 platform-settings PUT 的管理员凭据

加载 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md)。

## 可选的后续工作

- `data/` 下的知识 / 资源种子（不在 v1 模板中）
- 从 `theme-tokens.json` 完整消费 CSS 主题
- 更多人设角色 — 保持 slug 唯一，变更后重新运行同步
