[English](./smoke-checklist.md) | [简体中文](./smoke-checklist.zh-CN.md) | [繁體中文](./smoke-checklist.zh-TW.md)

# 冒煙清單

在 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) 的 Phase 1（預設堆疊）與 Phase 2（白標覆寫層）之後執行。

## 基礎設施

- [ ] 發佈已解壓，compose 或 Helm 部署回報服務健康（`docker compose ps` 或等價指令）。
- [ ] 登入 / 應用 URL 可存取（您設定的主機，例如 `https://hub.example.com`）。

## 品牌（Option B）

- [ ] 啟動頁與登入頁顯示來自 `branding/platform-settings.json` 的**您的** `product_name`（非上游預設產品字串）。
- [ ] Logo 可載入：`logo_url` 可存取（靜態掛載或上傳路徑）。
- [ ] `auth_login` / `auth_register` 標題與種子文案一致。
- [ ] 管理員可 **GET** 與種子一致的平台設定（發佈支援的相關欄位）。

## Persona pack

- [ ] `PERSONA_TEMPLATE_CONFIG_PATH` 指向您掛載的 `persona-templates.json`。
- [ ] 使用 `replace_platform` 的一次性同步已完成（先 dry-run，再套用）。
- [ ] 人設選擇器**僅**列出您 pack 中的範本（無完整預設目錄 clutter）。
- [ ] 預設角色與 JSON 中 `is_default: true` 的範本一致（例如 **General**）。

## 部署前驗證

- [ ] `./scripts/validate-artifacts.sh` 在 fork 上結束代碼為 0。

## OAuth（僅當執行了 Phase 1.5）

- [ ] `OAUTH_PROVIDER_ENABLED=true` 且 issuer URL 與主機一致。
- [ ] OAuth authorize 端點不傳回 “provider disabled” 404。

## 冷路徑標準（產品）

新客戶或 **AI 代理** 應能在**不編輯 chatkit 原始碼**的情況下，憑：發佈 URL、本儲存庫路徑及其提供的憑證，到達品牌化登入介面與修剪後的人設 pack。
