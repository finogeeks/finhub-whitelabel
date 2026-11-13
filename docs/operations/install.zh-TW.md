[English](./install.md) | [简体中文](./install.zh-CN.md) | [繁體中文](./install.zh-TW.md)

# 安裝與首次啟動

說明 FinHub 離線發佈套件中腳本的**預設地端部署路徑**。腳本名稱與順序固定；compose 檔名可能因版本略有不同——若發佈 README 指定其他檔案，以其為準。

## 前置條件

- Docker + Compose v2、`openssl`、`bun`
- 供應商下發的部署授權（`DEPLOYMENT_LICENSE_KEY`、`DEPLOYMENT_LICENSE_CIPHER`）
- 生產環境需設定 LLM 端點與 `LLM_API_KEY`（開發用 mock LLM 無法承載真實使用者）

## 引導順序

```bash
cd <release-root>   # 含 .env.example 與 scripts/ 的目錄

./scripts/init-env.sh
./scripts/gen-secrets.sh
```

1. **`init-env.sh`** — 若無 `.env` 則從 `.env.example` 建立；補齊 Hermes/FinSAFE 艦隊預設值；在 `services/platform/identity-service/keys/` 產生 **JWT PEM** 並寫入 `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY` / `IDP_PUBLIC_KEY`；缺失時產生 A2A 委派金鑰；授權為空時提示。

2. **`gen-secrets.sh`** — 透過 `env-secrets-cli.ts` 冪等寫入機器密鑰；**不回顯取值**；`.env` 設為 `600`。需要 `bun`。

**維運編輯 `.env`**（人工提供）：

- `DEPLOYMENT_LICENSE_KEY`、`DEPLOYMENT_LICENSE_CIPHER`
- `LLM_API_KEY`（及模型/供應商，如非預設）
- 非本機映像時 `CHATKIT_REGISTRY` / `CHATKIT_VERSION`
- 對外存取的 `APP_URL` 等

```bash
./scripts/preflight-env.sh
```

若仍有預留字或授權缺失，僅列出**變數名稱**。

離線套件：

```bash
./scripts/load-images.sh
```

啟動：

```bash
./scripts/fleet.sh up -d
```

`fleet.sh` 預設執行與上相同的預檢（除非略過），啟動 compose 並依發佈說明等待 identity/fleet-manager、協調租戶 claw。

```bash
./scripts/doctor.sh
./scripts/doctor.sh --logs
```

## 地端部署：預設零外部依賴

- **Turnstile** — 選用。 air-gapped 註冊請勿設定 `TURNSTILE_SECRET`、`TURNSTILE_HOSTNAMES`、`TURNSTILE_SITEKEY`。
- **finops-staff 通知** — 未設定前不外呼（見 [finops-notifications](./finops-notifications.zh-TW.md)）。
- **Slack / 飛書等** — 對話能力不依賴外聯。

## `FLEET_SKIP_PREFLIGHT`（僅非生產）

```bash
FLEET_SKIP_PREFLIGHT=1 ./scripts/fleet.sh up -d
```

會印出：

```text
⚠️  FLEET_SKIP_PREFLIGHT=... — skipping scripts/preflight-env.sh
    (dev/drill/dogfood only; production must run preflight + real license)
```

僅用於工程檢出、演練套件或內部 dogfood，且維運接受預留字/授權風險。**客戶生產環境禁止使用。**

## 啟動之後

- 白標：[`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md)
- 冒煙：[`docs/smoke-checklist.md`](../smoke-checklist.zh-TW.md)
- 選用 FinOps：[finops-staff](./finops-staff.zh-TW.md)
- 選用郵件（Reloop）：[郵件渠道](./email-channel.zh-TW.md)

## 冒煙（API）

發佈樹若有 `scripts/test-e2e-api.sh` 可執行；否則透過閘道 URL（compose 文件中常見 `26100`）完成登入與對話驗證。
