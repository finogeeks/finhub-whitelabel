[English](./persona-pack-pin.md) | [简体中文](./persona-pack-pin.zh-CN.md) | [繁體中文](./persona-pack-pin.zh-TW.md)

# Persona pack 固定

如何固定 `persona-templates.json` 并运行一次性 **replace**，使人设选择器仅显示您的 pack。

## Classic 与白标

| | Default stack | White-label (this repo) |
|---|---------------|-------------------------|
| Pack JSON | Bundled default in chart/image | **This repo** → mount / ConfigMap |
| `PERSONA_TEMPLATE_CONFIG_PATH` | Unset (bundled) | **Always set** to mounted pack path |
| Boot `seedTemplates` | `upsert` / `insert_missing` | Same — **never** `replace_platform` on boot |
| One-shot prune | Do **not** run `replace_platform` | Run when pack changes or on first white-label deploy |

若您只运行一次 prune 但启动仍看到完整默认目录，下次重启可能重新导入额外角色。**白标必须固定**。

## 固定 vs 修剪

| Mechanism | When | What it does |
|-----------|------|--------------|
| **Pin** (`PERSONA_TEMPLATE_CONFIG_PATH`) | Always on `persona-service` | Every boot seeds from your pack file (upsert) |
| **Prune Job / compose profile** | Once per pack version (or after pack edits) | `replace_platform`: upsert pack slugs, delete orphan **platform** templates |

## 安全流程

1. 将 `PERSONA_TEMPLATE_CONFIG_PATH` 设为挂载路径（见 `deploy/compose/` 或 `deploy/helm/`）。
2. **先 dry-run** — 向同步 CLI 传入 `--dry-run`（Compose `persona-templates-sync` 或 Helm `personaTemplateSyncJob.extraArgs`）。
3. 使用与固定**相同的路径**应用 `replace_platform`。
4. 确认选择器仅显示您的模板；默认角色应与 JSON 中 `is_default: true` 的模板一致（例如 **General**）。

## 同步二进制（仅离线发布）

该工具随 **chatkit / FinHub 离线发布**提供，不在本仓库：

```text
/app/bin/sync-platform-persona-templates
```

您的 pack 文件必须设置 `"sync_mode": "replace_platform"`。Compose 与 Helm 封装会调用此二进制；服务名与 profile 请遵循发布 README。

这次修剪不会同步或删除预置技能。**管理端 → 同步预置技能**是 skill-service 的 `POST /admin/skills/sync-preset`。Compose profile 名 `persona-skill` 是人设栈，不是那个按钮。见 [`admin-and-whitelabel.zh-CN.md`](./admin-and-whitelabel.zh-CN.md)。

### 内置路径保护

当解析的配置为**内置**默认 `config/persona-templates.json` 时，CLI 会拒绝 `replace_platform`，除非传入 **`--i-know`**。白标部署必须使用**外部**路径（本仓库的 `persona-templates.json`）。切勿在共享多租户默认部署上对内置默认运行 replace。

## 数据库安全

- 修剪范围：仅 `tenantId IS NULL` 的平台模板。
- Agent 外键使用 **`onDelete: SetNull`** — 删除未使用的平台模板不会删除 agent；`templateId` 变为 null。
