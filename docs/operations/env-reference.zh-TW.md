[English](./env-reference.md) | [简体中文](./env-reference.zh-CN.md) | [繁體中文](./env-reference.zh-TW.md)

# 環境變數參考

發佈套件提供 `.env.example`。經 `init-env.sh` 複製為 `.env`。**切勿**將真實取值提交到 git 或貼在工單單裡。

圖例：**自動** = `gen-secrets.sh` 或 `init-env.sh` 在預留/空值時填入；**人工** = 維運或供應商；**機密** = 依憑證保管；**選用** = 預檢不要求必填。

## 引導流程

| 步驟 | 腳本 | 作用 |
|------|------|------|
| 1 | `init-env.sh` | `.env`、JWT PEM 檔案、缺失時的 A2A 金鑰、艦隊 URL 修正 |
| 2 | `gen-secrets.sh` | `.env` 中的機器密鑰 |
| 3 | 維運 | 授權、LLM、registry、公網 URL |
| 4 | `preflight-env.sh` | 仍有預留字或授權缺失則失敗 |

## 自動產生（`gen-secrets.sh`）

僅在值為空、已知開發預留字或長度不足時替換（規則見發佈套件 `env-secrets.ts`）：

| 變數 | 機密 | 說明 |
|----------|--------|-------|
| `VERIFY_CODE_SECRET` | 是 | 至少 32 位元組 |
| `INTERNAL_SERVICE_TOKEN` | 是 | 與艦隊內部 API 共用；finops-staff 存取 claw-fleet-manager |
| `OPEN_LOOP_WAKE_JWT_SECRET` | 是 | 至少 32 字元 |
| `FINSAFE_AUTH_TOKEN` | 是 | |
| `USER_SECRETS_KEK` | 是 | base64 32 位元組 KEK |
| `OIDC_STATE_COOKIE_SECRET` | 是 | |
| `SESSION_COOKIE_SECRET` | 是 | |
| `INTERNAL_APPROVAL_RESOLVE_TOKEN` | 是 | 空則產生 |
| `AI_INFRA_RS_CRON_INTERNAL_TOKEN` | 是 | 空則鏡像 `INTERNAL_SERVICE_TOKEN` |
| `SERVICE_API_KEYS` | 是 | 替換開發預留對應 |
| `A2A_DELEGATION_SIGNING_KEY` | 是 | `init-env.sh` / `fleet.sh` 亦會保證（≥32 位元組；既有則保留） |
| `FINOPS_STAFF_GENERIC_WEBHOOK_HMAC_SECRET` | 是 | 僅當 `.env` 中存在該鍵且值為空 |

**選用 finops 權杖**（僅當 `.env` 中**存在**該鍵時產生，含取消註解的 `KEY=` 存根）：

| 變數 | 機密 |
|----------|--------|
| `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` | 是 |
| `FINOPS_STAFF_INTERNAL_API_TOKEN` | 是 |
| `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` | 是 |

`gen-secrets` 完成後標準輸出可能列出 `Optional finops filled: …`（**僅名稱**）。

## 自動產生（`init-env.sh`，非 gen-secrets）

| 項 | 機密 | 說明 |
|------|--------|-------|
| `JWT_PRIVATE_KEY`、`JWT_PUBLIC_KEY`、`IDP_PUBLIC_KEY` | 是 | 自 `identity-service/keys/` PEM 寫入 `.env` |
| Hermes 預設項 | 否 | 如缺失時 `FINSAFE_SKIP_LOCAL_SERVER=0`、`HERMES_EXECUTION_POSTURE=confined` |

## 必須人工

| 變數 | 機密 | 說明 |
|----------|--------|-------|
| `DEPLOYMENT_LICENSE_KEY` | 是 | **僅供應商** — 不產生 |
| `DEPLOYMENT_LICENSE_CIPHER` | 是 | **僅供應商** — 不產生 |

授權缺失或無效 → identity-service 拒絕啟動。

## 生產常見（人工）

| 變數 | 機密 | 預檢 |
|----------|--------|-----------|
| `LLM_API_KEY` | 是 | 允許為空（真實推論需填寫） |
| `CHATKIT_REGISTRY`、`CHATKIT_VERSION` | 否 | 拉取映像 |
| `APP_URL`、Cookie 網域 | 否 | 瀏覽器公網 URL |
| `ADMIN_EMAILS` | 否 | 初始管理員 |

## 選用人工（整合）

| 變數 | 機密 | 場景 |
|----------|--------|------|
| `TURNSTILE_SECRET`、`TURNSTILE_HOSTNAMES`、`TURNSTILE_SITEKEY` | 是（密鑰） | 公網註冊 |
| `FINOPS_STAFF_SLACK_WEBHOOK_URL` | 是 | Slack 通知 |
| `FINOPS_STAFF_NOTIFY_MIN_SEVERITY` | 否 | 通知門檻：`info`、`warning` 或 `critical`（預設 `warning`；無效或空 → `warning`）— 見 [finops-notifications](./finops-notifications.zh-TW.md) |
| 各通道 URL/密碼 | 是 | 見 [finops-notifications](./finops-notifications.zh-TW.md) — 除上文 HMAC 外不由 gen-secrets 產生 |

## finops-staff 文件預設（客戶姿態）

啟用 finops-staff 時建議在 `.env` 保持：

```bash
FINOPS_STAFF_POLICY_MODE=readonly
FINOPS_STAFF_AUTO_ACT_DISABLED=true
FINOPS_STAFF_CLOSED_LOOP_ENABLED=false
```

Compose 覆寫（`${FINOPS_STAFF_AUTO_ACT_DISABLED:-true}` / `${FINOPS_STAFF_CLOSED_LOOP_ENABLED:-false}`）與 Helm（`finopsStaff.autoActDisabled: true`、`finopsStaff.closedLoopEnabled: false`，除非覆寫否則始終寫入 Pod env）均與上表一致。已在發佈語意 `cb3e6418` 核對。

## Helm 上的 finops-staff（認證與通知）

生產環境優先使用 **`finopsStaff.existingSecret`**，勿在 values 中寫明文令牌。Chart 透過 **`finopsStaff.secretKeys`** 讀取鍵名（預設如下）。**`finopsStaff.createSecret.enabled: true`** 僅用於開發／實驗室（由 Chart 渲染 Secret）。**`finopsStaff.notifyMinSeverity`** 為 `info`、`warning` 或 `critical`（預設 `warning`），與 compose 的 `FINOPS_STAFF_NOTIFY_MIN_SEVERITY` 一致。

| Helm 值 | 預設 Secret 鍵 | 等效 compose `.env` |
|---------|----------------|---------------------|
| `secretKeys.alertWebhookToken` | `alert_webhook_token` | `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` |
| `secretKeys.internalApiToken` | `internal_api_token` | `FINOPS_STAFF_INTERNAL_API_TOKEN` |
| `secretKeys.approvalWebhookToken` | `approval_webhook_token` | `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` |

範例：[`deploy/helm/values-finops-staff-auth.example.yaml`](../../deploy/helm/values-finops-staff-auth.example.yaml)。Alertmanager 透過 `bearer_token_file` 掛載同一 Secret — 見 [`deploy/helm/values-alertmanager-finops.example.yaml`](../../deploy/helm/values-alertmanager-finops.example.yaml) 與 [finops-staff](./finops-staff.zh-TW.md#helm-認證密鑰)。

## JWT 與授權

- **JWT** — 磁碟 PEM + `.env`；輪替見發佈套件說明。
- **授權** — 續約聯絡供應商；本套件不提供授權產生器。

完整存根列表：發佈樹 `.env.example` 第 11 節（finops）。
