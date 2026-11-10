[English](./customize.md) | [简体中文](./customize.zh-CN.md) | [繁體中文](./customize.zh-TW.md)

# 自訂白標 FinHub

典型 v1 部署的**種子**改動在**本儲存庫**完成 — 無需 fork chatkit-web 或 chatkit-middleware。堆疊起來之後，日常的 Logo、文案和預置技能在 FinHub 管理端修改。邊界見 [`admin-and-whitelabel.zh-TW.md`](./admin-and-whitelabel.zh-TW.md)。

## 1. 產品名稱與登入主文案

編輯 [`branding/platform-settings.json`](../branding/platform-settings.json)：

- `product_name`、`login_hero` — 線上設定 PUT 唯一會儲存的欄位。之後再跑種子 PUT，會覆蓋**管理端 → 平台設定**裡儲存的同名欄位。
- `auth_login`、`auth_register`、`family_line`、`auth_show_marquee`、`document_titles`、`logo_url` — 仍參與本儲存庫驗證和靜態預覽。線上 PUT 會丟掉這些鍵。瀏覽器標題跟著中文產品名走。

編輯後執行 `./scripts/validate-artifacts.sh`。

## 2. Logo 與靜態品牌

替換 [`branding/assets/`](../branding/assets/) 下的檔案，供本機預覽（方標、字標、favicon、OG）。

執行中的登入標是在**管理端 → 平台設定**上傳的檔案（`/platform-uploads/...`）。掛載 `branding/assets/` 不會寫入 `logo_url`。再次執行種子 PUT 不會清掉已上傳的 Logo。

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
