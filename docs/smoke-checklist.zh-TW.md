[English](./smoke-checklist.md) | [简体中文](./smoke-checklist.zh-CN.md) | [繁體中文](./smoke-checklist.zh-TW.md)

# 冒煙清單

在 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) 的 Phase 1（預設堆疊）與 Phase 2（白標覆寫層）之後執行。

## 基礎設施

- [ ] 發佈已解壓，compose 或 Helm 部署回報服務健康（`docker compose ps` 或等價指令）。
- [ ] 登入 / 應用 URL 可存取（您設定的主機，例如 `https://hub.example.com`）。

## 品牌（Option B）

- [ ] 啟動頁與登入頁顯示來自 `branding/platform-settings.json` 的**您的** `product_name` 和 `login_hero`（非上游預設產品字串）。
- [ ] 登入標是在**管理端 → 平台設定**上傳的檔案。僅有種子裡的 `logo_url` 不會生效。見 [`admin-and-whitelabel.zh-TW.md`](./admin-and-whitelabel.zh-TW.md)。
- [ ] `GET /platform/settings` 的 `product_name` 與 `login_hero` 與種子一致。瀏覽器標題跟著中文產品名。`auth_login` / `auth_register` 只用在本機預覽。

## Persona pack

- [ ] `PERSONA_TEMPLATE_CONFIG_PATH` 指向您掛載的 `persona-templates.json`。
- [ ] 使用 `replace_platform` 的一次性同步已完成（先 dry-run，再套用）。
- [ ] 人設選擇器**僅**列出您 pack 中的範本（無完整預設目錄 clutter）。
- [ ] 預設角色與 JSON 中 `is_default: true` 的範本一致（例如 **General**）。

## 部署前驗證

- [ ] `./scripts/validate-artifacts.sh` 在 fork 上結束代碼為 0。

## 郵件渠道（僅當啟用 Reloop connector）

- [ ] `email-connector` 健康（埠 `26464` 上 `GET /internal/health` 或發佈包 doctor）。
- [ ] Admin → 渠道 → 郵件已儲存；`POST /internal/test-connection` 成功（服務權杖）。
- [ ] 狀態含 `transport_ready`、`domain_verified`（Webhook 就緒時含 `webhook_configured`）。
- [ ] API 冒煙：provision → bind → 入站郵件更新 `last_inbound_at`（見 [郵件渠道](./operations/email-channel.zh-TW.md)）。

## OAuth（僅當執行了 Phase 1.5）

- [ ] `OAUTH_PROVIDER_ENABLED=true` 且 issuer URL 與主機一致。
- [ ] OAuth authorize 端點不傳回 “provider disabled” 404。

## 冷路徑標準（產品）

新客戶或 **AI 代理** 應能在**不編輯 chatkit 原始碼**的情況下，憑：發佈 URL、本儲存庫路徑及其提供的憑證，到達品牌化登入介面與修剪後的人設 pack。
