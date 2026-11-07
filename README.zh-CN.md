[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# FinHub 白标客户模板

## FinHub 是什么

**企业智能体的管理中心。** FinHub 让 IT 团队决定谁能使用哪些智能体和工具，并为每次对话保留不可修改的记录。它运行在企业自己的服务器上，可使用我们的智能体引擎 FinClaw，也可使用你们自己的引擎。

了解更多：[finaios.ai 上的 FinHub 产品页](https://finaios.ai/zh-hans/products/finhub/)。

面向公开 fork 或克隆的模板，用于部署您自己的 **FinHub** 实例。在本仓库中定制品牌与人设包，然后将您的离线发布 tarball URL 与本目录树交给部署 **AI 代理**。

**FinHub** 是对客户展示的产品名称。上游离线发布包中的镜像或 compose 名称仍可能使用 `chatkit`，这是预期行为。

> **AI 代理：**安装与部署请参阅 [`skills/finhub-deploy/SKILL.md`](./skills/finhub-deploy/SKILL.md)，不要仅依据本 README。

## 快速开始

1. **前置条件** — Docker Engine + Compose v2（或 Kubernetes + Helm）；来自供应商的离线 FinHub/chatkit 发布 tarball URL；堆栈就绪后用于平台设置种子的管理员凭据。
2. **克隆** — `git clone https://github.com/finogeeks/finhub-whitelabel`（或将本仓库用作 GitHub 模板）。
3. **定制** — 参阅 [`docs/customize.md`](./docs/customize.md)。
   - 产品文案 + 认证界面 → [`branding/platform-settings.json`](./branding/platform-settings.json)
   - Logo → [`branding/assets/`](./branding/assets/)
   - 人设入门包 → [`persona-templates.json`](./persona-templates.json)
   - 主机 / TLS → [`deploy/compose/`](./deploy/compose/) 或 [`deploy/helm/`](./deploy/helm/)
4. **校验** — `./scripts/validate-artifacts.sh`（无需网络）。
5. **部署** — 向 **AI 代理** 提供发布 URL、本 fork 路径及凭据。加载 [`skills/finhub-deploy/SKILL.md`](./skills/finhub-deploy/SKILL.md) 并按 Phase 1 → Phase 2 执行（仅在需要时执行 Phase 1.5 OAuth）。
6. **冒烟** — [`docs/smoke-checklist.md`](./docs/smoke-checklist.md)。

## 仓库结构

```
README.md
branding/
  platform-settings.json       # Option B auth / product chrome seed
  theme-tokens.json            # design SoT only (_consumed_by_chatkit: false)
  assets/                      # your mark, wordmark, favicon, OG
  README.md
persona-templates.json         # starter pack (pin + one-shot replace)
deploy/
  compose/                     # mounts, PERSONA_TEMPLATE_CONFIG_PATH, sync profile
  helm/                        # values + ConfigMap stubs
  oauth-provider.env.example   # opt-in OAuth only
docs/
  persona-pack-pin.md
  customize.md
  smoke-checklist.md
skills/
  finhub-deploy/SKILL.md       # primary agent entrypoint
scripts/
  validate-artifacts.sh        # Soft P0: presence + JSON parse
```

## 参考部署

已完成 FinHub 皮肤的线上实例：[finhub.finaios.ai](https://finhub.finaios.ai)（Finogeeks 参考示例 — 并非您 fork 的必选主机名）。产品页：发布后见于 finaios.ai 上的 FinHub。

## Pack 同步（摘要）

人设 **replace** 使用**离线发布**镜像内的 `/app/bin/sync-platform-persona-templates` — 本仓库不重新实现该逻辑。将 `PERSONA_TEMPLATE_CONFIG_PATH` 固定为您挂载的 `persona-templates.json`，然后运行 [`docs/persona-pack-pin.md`](./docs/persona-pack-pin.md) 中记录的 compose profile 或 Helm Job。

## 本仓库不包含

- 不在 chatkit-web 或 chatkit-middleware 内的 FinHub 命名补丁
- 部署配置中无必需的 `finhub.finaios.ai` 主机默认值
- 无应用源代码 — 仅种子、挂载与部署覆盖层

## 支持路径

在此定制制品 → **AI 代理** 以您的发布 URL 运行 `skills/finhub-deploy` → 冒烟清单。OAuth 与高级 embed RP 连线为可选（[`deploy/oauth-provider.env.example`](./deploy/oauth-provider.env.example)）。
