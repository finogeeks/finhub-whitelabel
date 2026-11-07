[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Docker Compose 覆寫層

白標覆寫：人設固定、platform settings 檔案掛載、品牌資源掛載至 `/static/branding`。需要來自**離線 chatkit / FinHub 發佈套件**的生產 compose 檔案（本儲存庫不附帶）。

文件預設範例主機：**`hub.example.com`** — 請為環境設定 ingress / `ADMIN_BASE`。

## 檔案

| File | Role |
|------|------|
| `docker-compose.whitelabel.override.yml` | Persona pin, platform settings mount, `/static/branding` assets |

## 環境路徑

```bash
export WL_PERSONA_PACK_HOST_PATH=/path/to/finhub-whitelabel/persona-templates.json
export WL_PLATFORM_SETTINGS_HOST_PATH=/path/to/finhub-whitelabel/branding/platform-settings.json
export WL_BRANDING_ASSETS_HOST_PATH=/path/to/finhub-whitelabel/branding/assets
```

人設同步時，上游可能使用 `PERSONA_TEMPLATE_PACK_HOST_PATH` — 請設為同一 pack 檔案。

## 人設一次性同步（先 dry-run）

```bash
export PERSONA_TEMPLATE_PACK_HOST_PATH="$WL_PERSONA_PACK_HOST_PATH"

docker compose -f docker-compose.prod.yml \
  -f /path/to/finhub-whitelabel/deploy/compose/docker-compose.whitelabel.override.yml \
  --profile persona-skill --profile persona-templates-sync \
  run --rm persona-templates-sync -- --dry-run
```

移除 `--dry-run` 以透過發佈映像內的 `/app/bin/sync-platform-persona-templates` 套用 `replace_platform`。

## Platform settings 種子

堆疊就緒後：

```bash
export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
  -H "Content-Type: application/json" \
  -d @"$WL_PLATFORM_SETTINGS_HOST_PATH"
```

## 穩態執行

```bash
docker compose -f docker-compose.prod.yml \
  -f deploy/compose/docker-compose.whitelabel.override.yml \
  up -d
```

除非您打算固定 pack 與品牌檔案，否則不要在預設（非白標）compose 上新增此覆寫層。
