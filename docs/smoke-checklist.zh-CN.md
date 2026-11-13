[English](./smoke-checklist.md) | [简体中文](./smoke-checklist.zh-CN.md) | [繁體中文](./smoke-checklist.zh-TW.md)

# 冒烟清单

在 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) 的 Phase 1（默认堆栈）与 Phase 2（白标覆盖层）之后运行。

## 基础设施

- [ ] 发布已解压，compose 或 Helm 部署报告服务健康（`docker compose ps` 或等价命令）。
- [ ] 登录 / 应用 URL 可访问（您配置的主机，例如 `https://hub.example.com`）。

## 品牌（Option B）

- [ ] 启动页与登录页显示来自 `branding/platform-settings.json` 的**您的** `product_name` 和 `login_hero`（非上游默认产品字符串）。
- [ ] 登录标是在**管理端 → 平台设置**上传的文件。仅有种子里的 `logo_url` 不会生效。见 [`admin-and-whitelabel.zh-CN.md`](./admin-and-whitelabel.zh-CN.md)。
- [ ] `GET /platform/settings` 的 `product_name` 与 `login_hero` 与种子一致。浏览器标题跟着中文产品名。`auth_login` / `auth_register` 只用于本地预览。

## Persona pack

- [ ] `PERSONA_TEMPLATE_CONFIG_PATH` 指向您挂载的 `persona-templates.json`。
- [ ] 使用 `replace_platform` 的一次性同步已完成（先 dry-run，再应用）。
- [ ] 人设选择器**仅**列出您 pack 中的模板（无完整默认目录 clutter）。
- [ ] 默认角色与 JSON 中 `is_default: true` 的模板一致（例如 **General**）。

## 部署前校验

- [ ] `./scripts/validate-artifacts.sh` 在 fork 上退出码为 0。

## 邮件渠道（仅当启用 Reloop connector）

- [ ] `email-connector` 健康（端口 `26464` 上 `GET /internal/health` 或发布包 doctor）。
- [ ] Admin → 渠道 → 邮件已保存；`POST /internal/test-connection` 成功（服务令牌）。
- [ ] 状态含 `transport_ready`、`domain_verified`（Webhook 就绪时含 `webhook_configured`）。
- [ ] API 冒烟：provision → bind → 入站邮件更新 `last_inbound_at`（见 [邮件渠道](./operations/email-channel.zh-CN.md)）。

## OAuth（仅当运行了 Phase 1.5）

- [ ] `OAUTH_PROVIDER_ENABLED=true` 且 issuer URL 与主机一致。
- [ ] OAuth authorize 端点不返回 “provider disabled” 404。

## 冷路径标准（产品）

新客户或 **AI 代理** 应能在**不编辑 chatkit 源代码**的情况下，凭：发布 URL、本仓库路径及其提供的凭据，到达品牌化登录界面与修剪后的人设 pack。
