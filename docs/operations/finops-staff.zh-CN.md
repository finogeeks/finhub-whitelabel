[English](./finops-staff.md) | [简体中文](./finops-staff.zh-CN.md) | [繁體中文](./finops-staff.zh-TW.md)

# finops-staff（可选受监督自愈）

**finops-staff** 为可选平台服务：告警接入、有界诊断、**人工审批**后的修复。不在用户对话路径上——停止或禁用**不会**影响 FinHub 对话服务。

客户默认：**不启用**（无 compose profile / `finopsStaff.enabled=false`）。

## 启用

**Docker Compose**

```bash
# 在 .env.example 取消 finops 存根注释、设置策略默认，再 gen-secrets 生成令牌
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff up -d
```

**Helm**

```bash
helm upgrade --install <release> <chart-path> \
  --set finopsStaff.enabled=true \
  --set finopsStaff.policyMode=readonly
```

Compose（`docker-compose.finops-staff.yml`）与 Helm（`finopsStaff` 值及渲染后的 env）均默认**关闭 auto-act**与**关闭 closed-loop**：`FINOPS_STAFF_AUTO_ACT_DISABLED=true`、`FINOPS_STAFF_CLOSED_LOOP_ENABLED=false`（除非运维覆盖）。发布包行为已在 `eaf6b93b` 核对。

| 项 | 值 |
|------|--------|
| 默认端口 | `26116` |
| 健康检查 | `GET /health`（公开） |
| 告警入口 | `POST /webhooks/alertmanager` |
| 诊断/执行 | `POST /internal/*` |
| 审批 | `POST /webhooks/approval` |
| 审计 | `GET /internal/audit` |
| Doctor JSON | `GET /internal/doctor` |

`.env` 中的 `INTERNAL_SERVICE_TOKEN` 供 finops-staff 访问 claw-fleet-manager（见发布包 `docker-compose.finops-staff.yml`）。

## Doctor 快照（`GET /internal/doctor`）

只读 JSON（`finops-doctor/v1`），用于升级后姿态核对 — 不能替代发布包 `scripts/doctor.sh`。

| 字段 | 客户默认 | 含义 |
|------|----------|------|
| `auto_act_disabled` | `true` | 自动修复动作保持关闭 |
| `closed_loop_enabled` | `false` | 闭环控制器保持关闭 |

另含 `notify_channels_configured`、`notify_channels_listed` 与 `notify_startup_warnings`。可在不启用 auto-act 的情况下确认断路开关与通知配置。

## 策略模式

| 模式 | 诊断 | 修复 |
|------|----------|-----------|
| `readonly`（默认） | 是 | 拒绝 |
| `supervised` | 是 | 白名单动作；**须审批** |
| `full` | 是 | 更广白名单；生产副本写入另有限制 |

仅在 SecAI/安全团队批准后将 disposable 堆栈升为 `supervised`。客户文档**不**涵盖启用无人值守 auto-act 或 closed-loop。

## 文档化断路开关（保持默认）

```bash
FINOPS_STAFF_AUTO_ACT_DISABLED=true
FINOPS_STAFF_CLOSED_LOOP_ENABLED=false
```

请勿为客户生产环境启用自动舰队 PATCH 或 closed-loop 周期任务。

## 告警 → 诊断 → 待修复 → 审批

1. **Alertmanager** 调用 `http://<finops-staff>:26116/webhooks/alertmanager`，可选 `Authorization: Bearer <FINOPS_STAFF_ALERT_WEBHOOK_TOKEN>` 或头 `x-finops-alert-token`。

2. **入口模式**（生产告警流至多选一，演练包除外）：
   - `FINOPS_STAFF_ALERT_DIAGNOSE_ONLY=true` — 仅通知与诊断
   - `FINOPS_STAFF_ALERT_PENDING_REPAIR=true` — 需 `FINOPS_STAFF_POLICY_MODE=supervised`；根据带 `act`、`tenant_id`、`deployment_id` 标签的 firing 告警创建**待处理**白名单动作（不自动执行）

3. **人工审批** — `POST /webhooks/approval`，JSON 含 `decision_id`、`approved`、`actor`；若配置 `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` 则带头 `x-finops-approval-token`：

```bash
curl -sS -X POST "https://<finops-host>:26116/webhooks/approval" \
  -H 'Content-Type: application/json' \
  -H 'x-finops-approval-token: <FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN>' \
  -d '{"decision_id":"<id>","approved":true,"actor":"oncall"}'
```

4. **执行** — 审批后对同一 `decision_id` 再调用 `POST /internal/act`。

5. **冷却** — `FINOPS_STAFF_RESTART_COOLDOWN_MS`（默认 `300000`）限制同部署重启频率。

6. **审计** — 记录 `tenant_id`、`actor`、`decision_id`、`policy_mode`、fleet 路径；`GET /internal/audit` 查询。

## 白名单动作（supervised / full）

| 动作 | 说明 |
|-----|-------|
| `log_rotate` | 仅策略确认；无主机 exec |
| `fleet_restart` | 经 claw-fleet-manager |
| `fleet_set_desired_replicas` | 默认非生产；生产需发布包中 explicit SecAI 标志 |

**禁止 finops-staff：** 删 PVC、数据库 failover、缩容至零、`kubectl exec`、批量 `reconcile-all`、绕过 identity 的管理接口。

## 令牌（Webhook 暴露时建议）

在 `.env` 取消存根后执行 `./scripts/gen-secrets.sh`：

| 变量 | 用途 |
|----------|---------|
| `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` | Alertmanager |
| `FINOPS_STAFF_INTERNAL_API_TOKEN` | `POST /internal/*`（health 仍公开） |
| `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` | 可选审批 Webhook 门控 |

## Prometheus

将 `FINOPS_STAFF_PROMETHEUS_URL` 设为集群内 Prometheus。compose 默认 `http://chatkit-prometheus-dogfood:9090` 仅用于供应商内部 dogfood——客户环境必须覆盖。

## 通知

外呼可选：[finops-notifications](./finops-notifications.zh-CN.md)。通道失败隔离（诊断成功时仍返回 200）。

## 下线

```bash
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff down
```

对话与核心平台继续运行。

## 相关

- [安装](./install.zh-CN.md) · [环境参考](./env-reference.zh-CN.md) · [日常运维](./day-2-ops.zh-CN.md)
