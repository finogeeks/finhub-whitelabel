[English](./customize.md) | [简体中文](./customize.zh-CN.md) | [繁體中文](./customize.zh-TW.md)

# 自訂白標 FinHub

典型 v1 部署中所有面向客戶的變更均在**本儲存庫**完成 — 無需 fork chatkit-web 或 chatkit-middleware。

## 1. 產品名稱與認證介面

編輯 [`branding/platform-settings.json`](../branding/platform-settings.json)：

- `product_name` — 顯示於啟動頁、登入頁與頂欄
- `login_hero`, `auth_login`, `auth_register` — 標題與副標題（zh/en）
- `family_line` — 認證頁頁尾行
- `logo_url` — 靜態掛載後的路徑（預設 `/static/branding/acme-mark.svg`）
- `document_titles` — 瀏覽器分頁標題

編輯後執行 `./scripts/validate-artifacts.sh`。

## 2. Logo 與靜態品牌

替換 [`branding/assets/`](../branding/assets/) 下的檔案：

- `acme-mark.svg` — 方形標記（可按需重新命名檔案；同步更新 `logo_url`）
- `acme-wordmark.svg`, `favicon.svg`, `og-acme.svg`

選用：跳過靜態檔案，透過管理員 **`PUT /admin/config/platform-settings/logo`** 上傳，然後將 `logo_url` 指向 `/platform-uploads/...`。

## 3. 人設入門包

編輯 [`persona-templates.json`](../persona-templates.json)：

- 一次性修剪請保持 `"sync_mode": "replace_platform"`
- 恰好一個範本設定 `"is_default": true`
- 使用 `template_format`：`soul_identity`，含 `soul_template` 與 `identity_template`
- `avatar_url` 可為空或指向您託管的頭像

固定與同步步驟見 [`persona-pack-pin.md`](./persona-pack-pin.md)。

## 4. 主機、TLS 與 ingress

- **Compose** — 在發佈 `.env` 與反向代理中設定公開 URL；種子化 platform settings 時使用 `ADMIN_BASE`（見 `deploy/compose/README.md`）。
- **Helm** — 在 `deploy/helm/values-whitelabel.yaml` 中覆寫 `ingress.hosts`（預設範例：`hub.example.com`）。

除非那就是您的真實生產主機，否則不要在 fork 中將廠商參考主機名稱硬編碼為**必需**預設值。

## 5. 主題權杖（選用）

[`branding/theme-tokens.json`](../branding/theme-tokens.json) 是團隊用的**設計 SoT**（`_consumed_by_chatkit: false`）。在上游平台主題支援出現之前，這些鍵可能不會被套用。

## 6. OAuth（選用）

僅在需要將 Identity 作為 OAuth 提供方用於 embed 或第三方 RP 時：

- 將 [`deploy/oauth-provider.env.example`](../deploy/oauth-provider.env.example) 複製到發佈環境
- 遵循 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) 中的 **Phase 1.5**

預設 FinHub 白標路徑**不**需要 OAuth。

## 7. 部署

向您的 **AI 代理** 提供：

- 離線發佈 tarball URL
- 本 fork 路徑
- 用於 platform-settings PUT 的管理員憑證

載入 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md)。

## 選用的後續工作

- `data/` 下的知識 / 資源種子（不在 v1 範本中）
- 從 `theme-tokens.json` 完整消費 CSS 主題
- 更多人設角色 — 保持 slug 唯一，變更後重新執行同步
