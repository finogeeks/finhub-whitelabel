[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# FinHub 白標客戶範本

## FinHub 是什麼

**企業 AI 代理的管理中心。** FinHub 讓 IT 團隊決定誰能使用哪些 AI 代理和工具，並為每次對話保留不可修改的紀錄。它運行在企業自己的伺服器上，可使用我們的 AI 代理引擎 FinClaw，也可使用你們自己的引擎。

了解更多：[finaios.ai 上的 FinHub 產品頁](https://finaios.ai/zh-hant/products/finhub/)。

面向公開 fork 或克隆的範本，用於部署您自己的 **FinHub** 執行個體。在本儲存庫中自訂品牌與人設包，然後將您的離線發佈 tarball URL 與本目錄樹交給部署 **AI 代理**。

**FinHub** 是對客戶展示的產品名稱。上游離線發佈套件中的映像或 compose 名稱仍可能使用 `chatkit`，這是預期行為。

> **AI 代理：**從 [`AGENTS.md`](./AGENTS.md) 開始；安裝與部署請參閱 [`skills/finhub-deploy/SKILL.md`](./skills/finhub-deploy/SKILL.md) 與 [`docs/agent-deploy-runbook.md`](./docs/agent-deploy-runbook.zh-TW.md)。

## 快速開始

1. **前置條件** — Docker Engine + Compose v2（或 Kubernetes + Helm）；來自供應商的離線 FinHub/chatkit 發佈 tarball URL；堆疊就緒後用於平台設定種子的管理員憑證。
2. **克隆** — `git clone https://github.com/finogeeks/finhub-whitelabel`（或將本儲存庫用作 GitHub 範本）。
3. **自訂** — 參閱 [`docs/customize.md`](./docs/customize.md)。
   - 產品文案 + 認證介面 → [`branding/platform-settings.json`](./branding/platform-settings.json)
   - Logo → [`branding/assets/`](./branding/assets/)
   - 人設入門包 → [`persona-templates.json`](./persona-templates.json)
   - 主機 / TLS → [`deploy/compose/`](./deploy/compose/) 或 [`deploy/helm/`](./deploy/helm/)
4. **驗證** — `./scripts/validate-artifacts.sh`（無需網路）。
5. **執行環境引導**（在發佈套件目錄）— `init-env.sh` → `gen-secrets.sh` → 授權與 `LLM_API_KEY` → `preflight-env.sh` → `fleet.sh up -d` → `doctor.sh`。見 [`docs/operations/install.zh-TW.md`](./docs/operations/install.zh-TW.md)。
6. **部署** — 向 **AI 代理** 提供發佈 URL、本 fork 路徑及憑證。載入 [`skills/finhub-deploy/SKILL.md`](./skills/finhub-deploy/SKILL.md) 並依 Phase 1 → Phase 2 執行（僅在需要時執行 Phase 1.5 OAuth 或 finops-staff）。
7. **冒煙** — [`docs/smoke-checklist.md`](./docs/smoke-checklist.zh-TW.md)。

## 儲存庫結構

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
AGENTS.md
docs/
  agent-deploy-runbook.zh-TW.md
  operations/                  # 安裝、環境變數、finops、通知、日常維運
  persona-pack-pin.md
  admin-and-whitelabel.md      # 管理端 Logo/文案、預置技能與種子的邊界
  customize.md
  smoke-checklist.md
skills/
  finhub-deploy/SKILL.md       # primary agent entrypoint
scripts/
  validate-artifacts.sh        # Soft P0: presence + JSON parse
```

## 參考部署

已完成 FinHub 外觀的線上執行個體：[finhub.finaios.ai](https://finhub.finaios.ai)（Finogeeks 參考範例 — 並非您 fork 的必選主機名）。產品頁：[finaios.ai 上的 FinHub](https://finaios.ai/zh-hant/products/finhub/)。

## 管理端與本儲存庫

白標部署之後，管理端仍可改 Logo、文案，並使用**同步預置技能**。種子 PUT 只寫入產品名和登入主文案，不會替換技能目錄，也不會清掉已上傳的 Logo。見 [`docs/admin-and-whitelabel.zh-TW.md`](./docs/admin-and-whitelabel.zh-TW.md)。

## Pack 同步（摘要）

人設 **replace** 使用**離線發佈**映像內的 `/app/bin/sync-platform-persona-templates` — 本儲存庫不重新實作該邏輯。將 `PERSONA_TEMPLATE_CONFIG_PATH` 固定為您掛載的 `persona-templates.json`，然後執行 [`docs/persona-pack-pin.md`](./docs/persona-pack-pin.md) 中記錄的 compose profile 或 Helm Job。

## 本儲存庫不包含

- 不在 chatkit-web 或 chatkit-middleware 內的 FinHub 命名修補
- 部署設定中無必需的 `finhub.finaios.ai` 主機預設值
- 無應用程式原始碼 — 僅種子、掛載與部署覆寫層
- 無離線映像與捆綁腳本（`init-env.sh`、`gen-secrets.sh`、`preflight-env.sh`、`fleet.sh`、`doctor.sh`）— 見供應商發佈套件與 [`AGENTS.md`](./AGENTS.md)

## 支援路徑

在此自訂製品 → 在發佈套件中完成環境引導（[`docs/operations/install.zh-TW.md`](./docs/operations/install.zh-TW.md)）→ **AI 代理** 執行 `skills/finhub-deploy` → 冒煙清單。選用 finops-staff 預設關閉（[`docs/operations/finops-staff.zh-TW.md`](./docs/operations/finops-staff.zh-TW.md)）。OAuth 與進階 embed RP 為選用（[`deploy/oauth-provider.env.example`](./deploy/oauth-provider.env.example)）。
