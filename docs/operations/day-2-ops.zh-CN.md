[English](./day-2-ops.md) | [简体中文](./day-2-ops.zh-CN.md) | [繁體中文](./day-2-ops.zh-TW.md)

# 日常运维（Day-2）

首次 `fleet.sh up` 成功后的维护任务。命令位于**发布树**；下列名称与当前 FinHub 离线发布一致。

## 升级

1. 向供应商获取新离线 tarball，阅读发行说明。
2. 变更前按下方**备份**。
3. 停止：`./scripts/fleet.sh down`（仅当发布说明要求时使用 `--keep-tenant-claws`）。
4. 替换镜像：`load-images.sh` 或按 README 拉取 registry。
5. 合并 `.env.example` 新增键——执行 `./scripts/init-env.sh`（已有 `.env` 时不覆盖）、`./scripts/gen-secrets.sh` 仅填新占位符。
6. `./scripts/preflight-env.sh` 后 `./scripts/fleet.sh up -d`。
7. `./scripts/doctor.sh` 与 [`smoke-checklist.md`](../smoke-checklist.zh-CN.md)。

若 compose 变更，按 [`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md) 重新叠加白标。

**Helm：** `helm upgrade` 更新 chart/values；`finopsStaff.enabled=true` 时单独滚动 finops-staff。

## 备份与恢复

| 资产 | 建议 |
|-------|----------|
| `.env` | 异地加密备份；含内联 JWT——**机密** |
| `services/platform/identity-service/keys/` | PEM；与 `.env` 一并备份 |
| Postgres / 会话数据 | 卷快照或发布包数据库运维说明 |
| 人设/品牌 | 以 `finhub-whitelabel` fork（git）为准 |
| 租户 claw 工作区 | `CLAW_FLEET_DOCKER_WORKSPACES_VOLUME` 命名卷（compose 默认常 `chatkit_workspaces`） |

恢复：停舰队 → 恢复卷/库 → 恢复 `.env` 与密钥 → `preflight` → `fleet up` → doctor。

## 日志

```bash
./scripts/fleet.sh logs -f
./scripts/fleet.sh ps
./scripts/doctor.sh --logs
```

Linux 管道缓冲时可：`LOG_FILES=./fleet.log ./scripts/fleet.sh up -d`。

可观测性（Prometheus、Alertmanager）为选配；仅启用 [finops-staff](./finops-staff.zh-CN.md) 时配置 finops Webhook。

## 密钥轮换

| 密钥 | 做法 |
|--------|----------|
| 机器密钥（`INTERNAL_SERVICE_TOKEN`、Cookie 密钥等） | 在 `.env` 写入新值，按发布说明顺序重启服务；复杂场景遵循供应商轮换手册 |
| `USER_SECRETS_KEK` | 若支持，使用 `USER_SECRETS_KEK_PREVIOUS` 与版本字段重加密 |
| JWT PEM | 按 init-env 流程重生成；用户需重新登录 |
| finops Webhook 令牌 | 更新 `.env`；占位符可再跑 `gen-secrets.sh`；重启 finops-staff |
| 部署许可证 | 供应商续期——仅编辑 `DEPLOYMENT_LICENSE_*` |

`gen-secrets.sh` **不会覆盖**非占位符的运维取值。

## finops-staff 生命周期

- 仅停 finops overlay 即可，不影响对话。
- 升级后保持 `FINOPS_STAFF_AUTO_ACT_DISABLED=true`、`FINOPS_STAFF_CLOSED_LOOP_ENABLED=false`（客户文档不提供启用 auto-act/closed-loop）。

## 拆除

```bash
./scripts/fleet.sh down
docker volume ls | grep chatkit   # 清理前确认
```

许可证归还/下线按合同约定。

## 故障排查

| 现象 | 检查 |
|---------|--------|
| identity-service 退出/不健康 | `DEPLOYMENT_LICENSE_*` 已设；预检通过 |
| 预检失败 | `./scripts/preflight-env.sh` 输出**变量名** |
| 仍为占位符密钥 | 重跑 `gen-secrets.sh` |
| Claw 长期 `starting` | `doctor.sh`；按发布说明调 `CLAW_FLEET_MANAGER_*` 超时 |
| LLM 错误 | `LLM_API_KEY`、`LLM_BASE_URL`、模型名 |
| finops Webhook 401 | Alertmanager Bearer 与 `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` 一致 |
| 无通知 | `FINOPS_STAFF_NOTIFY_CHANNELS` 列出通道但 URL 为空 → 启动警告 |
| 生产误用跳过预检 | 去掉 `FLEET_SKIP_PREFLIGHT`；使用真实许可证与 preflight |

启用 finops 时：`GET http://<host>:26116/internal/doctor`。

## 相关

- [安装](./install.zh-CN.md) · [环境参考](./env-reference.zh-CN.md) · [代理部署手册](../agent-deploy-runbook.zh-CN.md)
