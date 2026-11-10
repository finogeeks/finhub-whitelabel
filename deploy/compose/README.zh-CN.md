[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Docker Compose 覆盖层

白标覆盖：人设固定、platform settings 文件挂载、品牌资源挂载至 `/static/branding`。需要来自**离线 chatkit / FinHub 发布包**的生产 compose 文件（本仓库不附带）。

文档默认示例主机：**`hub.example.com`** — 请为环境配置 ingress / `ADMIN_BASE`。

## 文件

| File | Role |
|------|------|
| `docker-compose.whitelabel.override.yml` | Persona pin, platform settings mount, `/static/branding` assets |

## 环境路径

```bash
export WL_PERSONA_PACK_HOST_PATH=/path/to/finhub-whitelabel/persona-templates.json
export WL_PLATFORM_SETTINGS_HOST_PATH=/path/to/finhub-whitelabel/branding/platform-settings.json
export WL_BRANDING_ASSETS_HOST_PATH=/path/to/finhub-whitelabel/branding/assets
```

人设同步时，上游可能使用 `PERSONA_TEMPLATE_PACK_HOST_PATH` — 请设为同一 pack 文件。

## 人设一次性同步（先 dry-run）

```bash
export PERSONA_TEMPLATE_PACK_HOST_PATH="$WL_PERSONA_PACK_HOST_PATH"

docker compose -f docker-compose.prod.yml \
  -f /path/to/finhub-whitelabel/deploy/compose/docker-compose.whitelabel.override.yml \
  --profile persona-skill --profile persona-templates-sync \
  run --rm persona-templates-sync -- --dry-run
```

移除 `--dry-run` 以通过发布镜像内的 `/app/bin/sync-platform-persona-templates` 应用 `replace_platform`。

## Platform settings 种子

堆栈就绪后：

```bash
export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
  -H "Content-Type: application/json" \
  -d @"$WL_PLATFORM_SETTINGS_HOST_PATH"
```

这次只保存 `product_name` 和 `login_hero`。不会设置 Logo，也不会同步预置技能。见 [`docs/admin-and-whitelabel.zh-CN.md`](../../docs/admin-and-whitelabel.zh-CN.md)。

## 稳态运行

```bash
docker compose -f docker-compose.prod.yml \
  -f deploy/compose/docker-compose.whitelabel.override.yml \
  up -d
```

除非您打算固定 pack 与品牌文件，否则不要在默认（非白标）compose 上添加此覆盖层。
