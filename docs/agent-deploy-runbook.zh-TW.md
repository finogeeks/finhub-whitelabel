[English](./agent-deploy-runbook.md) | [简体中文](./agent-deploy-runbook.zh-CN.md) | [繁體中文](./agent-deploy-runbook.zh-TW.md)

# 代理部署執行手冊

供維運人員與編碼代理使用的端到端路徑：從離線發佈套件啟動**已授權**的 FinHub 堆疊，再套用本白標儲存庫。

## 前置條件

| 項目 | 說明 |
|------|------|
| 主機 | Docker Engine + Compose v2（或依發佈套件使用 Kubernetes + Helm） |
| 主機工具 | `openssl`、`bun`（部分離線套件已內建） |
| 供應商授權 | `DEPLOYMENT_LICENSE_KEY`、`DEPLOYMENT_LICENSE_CIPHER`（貼到 `.env`，不可自行產生） |
| LLM | 生產推論需設定 `LLM_API_KEY` 與供應商相關參數 |
| 白標 fork | 克隆 [`finogeeks/finhub-whitelabel`](https://github.com/finogeeks/finhub-whitelabel)；執行 `./scripts/validate-artifacts.sh` |

地端部署：除非公開註冊需要 Cloudflare Turnstile，否則**不要**設定 `TURNSTILE_*`。見[環境變數參考](./operations/env-reference.zh-TW.md)。

選用：Identity OAuth、finops-staff、**Reloop 郵件渠道**、監控（自建或重用 Prometheus 堆疊）、Turnstile、Slack — 均為 **opt-in**。監控接線見 [`docs/operations/monitoring.zh-TW.md`](./operations/monitoring.zh-TW.md)、[`skills/finhub-monitoring/SKILL.md`](../skills/finhub-monitoring/SKILL.md)。郵件見 [`docs/operations/email-channel.zh-TW.md`](./operations/email-channel.zh-TW.md)。

## 階段 A — 發佈套件執行環境（在 tarball 目錄內）

在發佈根目錄執行（通常含 `docker-compose.prod.yml` 與 `scripts/`）。

```bash
./scripts/init-env.sh
./scripts/gen-secrets.sh
# 編輯 .env：DEPLOYMENT_LICENSE_KEY、DEPLOYMENT_LICENSE_CIPHER、LLM_API_KEY、映像 registry/版本等
./scripts/preflight-env.sh
# 僅離線套件：
./scripts/load-images.sh
./scripts/fleet.sh up -d
./scripts/doctor.sh
```

細節見[安裝與首次啟動](./operations/install.zh-TW.md)。

**僅開發/演練**（非生產）：`FLEET_SKIP_PREFLIGHT=1 ./scripts/fleet.sh up -d` 會印出警告並略過 `preflight-env.sh`。

## 階段 B — 白標（本儲存庫）

依 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) Phase 2：

- 合併 `deploy/compose/docker-compose.whitelabel.override.yml`
- 固定人設包；可選 platform-settings PUT
- Kubernetes：`deploy/helm/values-whitelabel.yaml`

## 階段 C — 選用 finops-staff

受監督的診斷與**人工核准**修復，預設關閉。

```bash
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff up -d
```

Helm：`finopsStaff.enabled=true`，在 SecAI 核准前保持 `finopsStaff.policyMode=readonly`。見 [finops-staff](./operations/finops-staff.zh-TW.md)。

## 階段 C.5 — 郵件渠道（選用）

選用 Reloop 智能體郵件；**預設關閉**。自建 Reloop；在 Reloop 主控台手動註冊 Webhook。**Compose：** `email` profile + `.env` 對端 URL，重啟 identity-service 與 delivery（connector 未執行前郵件路徑 502）。**Helm：** 僅 `--set services.email-connector.enabled=true`（chart 接線對等服務與 nginx；關閉時不渲染路由）。見 [郵件渠道](./operations/email-channel.zh-TW.md)。

## 階段 D — 冒煙

階段 A、B 完成後執行 [`docs/smoke-checklist.md`](./smoke-checklist.zh-TW.md)。

## 代理核對清單

- [ ] 發佈 tarball 驗證通過（HTTP 200，檔名含預期 sha）
- [ ] `init-env.sh` → `gen-secrets.sh`（冪等；`.env` 權限 600）
- [ ] 授權與 LLM 由維運人員填寫（非腳本產生）
- [ ] `preflight-env.sh` 通過（非生產才允許記錄 `FLEET_SKIP_PREFLIGHT`）
- [ ] `fleet.sh up -d` 健康；`doctor.sh` 無關鍵異常
- [ ] 白標覆寫已套用；人設同步先 dry-run 再執行
- [ ] 冒煙清單完成
- [ ] 密鑰未進入 git、對話紀錄或日誌

## 相關文件

- [`AGENTS.md`](../AGENTS.md) — 代理入口索引
- [`docs/operations/day-2-ops.md`](./operations/day-2-ops.zh-TW.md) — 升級與維護
