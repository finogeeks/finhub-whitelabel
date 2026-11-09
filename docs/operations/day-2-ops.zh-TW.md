[English](./day-2-ops.md) | [简体中文](./day-2-ops.zh-CN.md) | [繁體中文](./day-2-ops.zh-TW.md)

# 日常維運（Day-2）

首次 `fleet.sh up` 成功後的維護工作。指令位於**發佈樹**；下列名稱與目前 FinHub 離線發佈一致。

## 升級

1. 向供應商取得新離線 tarball，閱讀發行說明。
2. 變更前依下方**備份**。
3. 停止：`./scripts/fleet.sh down`（僅當發佈說明要求時使用 `--keep-tenant-claws`）。
4. 替換映像：`load-images.sh` 或依 README 拉取 registry。
5. 合併 `.env.example` 新增鍵——執行 `./scripts/init-env.sh`（已有 `.env` 時不覆寫）、`./scripts/gen-secrets.sh` 僅填新預留字。
6. `./scripts/preflight-env.sh` 後 `./scripts/fleet.sh up -d`。
7. `./scripts/doctor.sh` 與 [`smoke-checklist.md`](../smoke-checklist.zh-TW.md)。

若 compose 變更，依 [`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md) 重新疊加白標。

**Helm：** `helm upgrade` 更新 chart/values；`finopsStaff.enabled=true` 時單獨滾動 finops-staff。

## 備份與還原

| 資產 | 建議 |
|-------|----------|
| `.env` | 異地加密備份；含內嵌 JWT——**機密** |
| `services/platform/identity-service/keys/` | PEM；與 `.env` 一併備份 |
| Postgres / 會話資料 | 磁碟區快照或發佈套件資料庫維運說明 |
| 人設/品牌 | 以 `finhub-whitelabel` fork（git）為準 |
| 租戶 claw 工作區 | `CLAW_FLEET_DOCKER_WORKSPACES_VOLUME` 命名磁碟區（compose 預設常 `chatkit_workspaces`） |

還原：停艦隊 → 還原磁碟區/資料庫 → 還原 `.env` 與金鑰 → `preflight` → `fleet up` → doctor。

## 日誌

```bash
./scripts/fleet.sh logs -f
./scripts/fleet.sh ps
./scripts/doctor.sh --logs
```

Linux 管道緩衝時可：`LOG_FILES=./fleet.log ./scripts/fleet.sh up -d`。

可觀測性（Prometheus、Alertmanager）為選用；僅啟用 [finops-staff](./finops-staff.zh-TW.md) 時設定 finops Webhook。

## 金鑰輪替

| 金鑰 | 做法 |
|--------|----------|
| 機器金鑰（`INTERNAL_SERVICE_TOKEN`、Cookie 金鑰等） | 在 `.env` 寫入新值，依發佈說明順序重啟服務；複雜情境遵循供應商輪替手冊 |
| `USER_SECRETS_KEK` | 若支援，使用 `USER_SECRETS_KEK_PREVIOUS` 與版本欄位重新加密 |
| JWT PEM | 依 init-env 流程重新產生；使用者需重新登入 |
| finops Webhook 權杖 | 更新 `.env`；預留字可再跑 `gen-secrets.sh`；重啟 finops-staff |
| 部署授權 | 供應商續約——僅編輯 `DEPLOYMENT_LICENSE_*` |

`gen-secrets.sh` **不會覆寫**非預留字的維運取值。

## finops-staff 生命週期

- 僅停 finops overlay 即可，不影響對話。
- 升級後保持 `FINOPS_STAFF_AUTO_ACT_DISABLED=true`、`FINOPS_STAFF_CLOSED_LOOP_ENABLED=false`（客戶文件不提供啟用 auto-act/closed-loop）。

## 拆除

```bash
./scripts/fleet.sh down
docker volume ls | grep chatkit   # 清理前確認
```

授權歸還/下線依合約約定。

## 故障排查

| 現象 | 檢查 |
|---------|--------|
| identity-service 退出/不健康 | `DEPLOYMENT_LICENSE_*` 已設；預檢通過 |
| 預檢失敗 | `./scripts/preflight-env.sh` 輸出**變數名稱** |
| 仍為預留字金鑰 | 重跑 `gen-secrets.sh` |
| Claw 長期 `starting` | `doctor.sh`；依發佈說明調 `CLAW_FLEET_MANAGER_*` 逾時 |
| LLM 錯誤 | `LLM_API_KEY`、`LLM_BASE_URL`、模型名 |
| finops Webhook 401 | Alertmanager Bearer 與 `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` 一致 |
| 無通知 | `FINOPS_STAFF_NOTIFY_CHANNELS` 列出通道但 URL 為空 → 啟動警告；或告警 `severity` 低於 `FINOPS_STAFF_NOTIFY_MIN_SEVERITY`（預設 `warning`）— 診斷成功、略過通知 |
| 生產誤用略過預檢 | 移除 `FLEET_SKIP_PREFLIGHT`；使用真實授權與 preflight |

啟用 finops-staff 時，以 `GET http://<host>:26116/internal/doctor`（認證方式見發佈套件說明）核對姿態。客戶環境應看到 `auto_act_disabled: true`、`closed_loop_enabled: false`，以及與 `.env` 一致的通知通道清單。

## 相關

- [安裝](./install.zh-TW.md) · [環境參考](./env-reference.zh-TW.md) · [代理部署手冊](../agent-deploy-runbook.zh-TW.md)
