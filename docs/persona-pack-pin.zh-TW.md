[English](./persona-pack-pin.md) | [简体中文](./persona-pack-pin.zh-CN.md) | [繁體中文](./persona-pack-pin.zh-TW.md)

# Persona pack 固定

如何固定 `persona-templates.json` 並執行一次性 **replace**，使人設選擇器僅顯示您的 pack。

## Classic 與白標

| | Default stack | White-label (this repo) |
|---|---------------|-------------------------|
| Pack JSON | Bundled default in chart/image | **This repo** → mount / ConfigMap |
| `PERSONA_TEMPLATE_CONFIG_PATH` | Unset (bundled) | **Always set** to mounted pack path |
| Boot `seedTemplates` | `upsert` / `insert_missing` | Same — **never** `replace_platform` on boot |
| One-shot prune | Do **not** run `replace_platform` | Run when pack changes or on first white-label deploy |

若您只執行一次 prune 但啟動仍看到完整預設目錄，下次重新啟動可能重新匯入額外角色。**白標必須固定**。

## 固定 vs 修剪

| Mechanism | When | What it does |
|-----------|------|--------------|
| **Pin** (`PERSONA_TEMPLATE_CONFIG_PATH`) | Always on `persona-service` | Every boot seeds from your pack file (upsert) |
| **Prune Job / compose profile** | Once per pack version (or after pack edits) | `replace_platform`: upsert pack slugs, delete orphan **platform** templates |

## 安全流程

1. 將 `PERSONA_TEMPLATE_CONFIG_PATH` 設為掛載路徑（見 `deploy/compose/` 或 `deploy/helm/`）。
2. **先 dry-run** — 向同步 CLI 傳入 `--dry-run`（Compose `persona-templates-sync` 或 Helm `personaTemplateSyncJob.extraArgs`）。
3. 使用與固定**相同的路徑**套用 `replace_platform`。
4. 確認選擇器僅顯示您的範本；預設角色應與 JSON 中 `is_default: true` 的範本一致（例如 **General**）。

## 同步二進位（僅離線發佈）

該工具隨 **chatkit / FinHub 離線發佈**提供，不在本儲存庫：

```text
/app/bin/sync-platform-persona-templates
```

您的 pack 檔案必須設定 `"sync_mode": "replace_platform"`。Compose 與 Helm 封裝會呼叫此二進位；服務名稱與 profile 請遵循發佈 README。

### 內建路徑保護

當解析的設定為**內建**預設 `config/persona-templates.json` 時，CLI 會拒絕 `replace_platform`，除非傳入 **`--i-know`**。白標部署必須使用**外部**路徑（本儲存庫的 `persona-templates.json`）。切勿在共享多租戶預設部署上對內建預設執行 replace。

## 資料庫安全

- 修剪範圍：僅 `tenantId IS NULL` 的平台範本。
- Agent 外鍵使用 **`onDelete: SetNull`** — 刪除未使用的平台範本不會刪除 agent；`templateId` 變為 null。
