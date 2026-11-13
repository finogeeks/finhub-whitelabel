[English](./agent-deploy-runbook.md) | [简体中文](./agent-deploy-runbook.zh-CN.md) | [繁體中文](./agent-deploy-runbook.zh-TW.md)

# 代理部署运行手册

面向运维人员与编码代理的端到端路径：从离线发布包拉起**已授权**的 FinHub 堆栈，再叠加本白标仓库。

## 前置条件

| 项目 | 说明 |
|------|------|
| 主机 | Docker Engine + Compose v2（或按发布包使用 Kubernetes + Helm） |
| 主机工具 | `openssl`、`bun`（部分离线包已内置） |
| 供应商许可证 | `DEPLOYMENT_LICENSE_KEY`、`DEPLOYMENT_LICENSE_CIPHER`（粘贴到 `.env`，不可自行生成） |
| LLM | 生产推理需配置 `LLM_API_KEY` 及提供商相关项 |
| 白标 fork | 克隆 [`finogeeks/finhub-whitelabel`](https://github.com/finogeeks/finhub-whitelabel)；执行 `./scripts/validate-artifacts.sh` |

本地部署：除非公网注册需要 Cloudflare Turnstile，否则**不要**设置 `TURNSTILE_*`。见[环境变量参考](./operations/env-reference.zh-CN.md)。

可选：Identity OAuth、finops-staff、**Reloop 邮件渠道**、监控（自建或复用 Prometheus 栈）、Turnstile、Slack — 均为 **opt-in**。监控接线见 [`docs/operations/monitoring.zh-CN.md`](./operations/monitoring.zh-CN.md)、[`skills/finhub-monitoring/SKILL.md`](../skills/finhub-monitoring/SKILL.md)。邮件见 [`docs/operations/email-channel.zh-CN.md`](./operations/email-channel.zh-CN.md)。

## 阶段 A — 发布包运行时（在 tarball 目录内）

在发布根目录执行（通常含 `docker-compose.prod.yml` 与 `scripts/`）。

```bash
./scripts/init-env.sh
./scripts/gen-secrets.sh
# 编辑 .env：DEPLOYMENT_LICENSE_KEY、DEPLOYMENT_LICENSE_CIPHER、LLM_API_KEY、镜像 registry/版本等
./scripts/preflight-env.sh
# 仅离线包：
./scripts/load-images.sh
./scripts/fleet.sh up -d
./scripts/doctor.sh
```

细节见[安装与首次启动](./operations/install.zh-CN.md)。

**仅开发/演练**（非生产）：`FLEET_SKIP_PREFLIGHT=1 ./scripts/fleet.sh up -d` 会打印警告并跳过 `preflight-env.sh`。

## 阶段 B — 白标（本仓库）

按 [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) Phase 2：

- 合并 `deploy/compose/docker-compose.whitelabel.override.yml`
- 固定人设包；可选 platform-settings PUT
- Kubernetes：`deploy/helm/values-whitelabel.yaml`

## 阶段 C — 可选 finops-staff

受监督的诊断与**人工审批**修复，默认关闭。

```bash
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff up -d
```

Helm：`finopsStaff.enabled=true`，在 SecAI 批准前保持 `finopsStaff.policyMode=readonly`。见 [finops-staff](./operations/finops-staff.zh-CN.md)。

## 阶段 C.5 — 邮件渠道（可选）

可选 Reloop 智能体邮件；**默认关闭**。自建 Reloop；在 Reloop 控制台手动注册 Webhook。**Compose：** `email` profile + `.env` 对端 URL，重启 identity-service 与 delivery（connector 未运行前邮件路径 502）。**Helm：** 仅 `--set services.email-connector.enabled=true`（chart 接线对端与 nginx；关闭时不渲染路由）。见 [邮件渠道](./operations/email-channel.zh-CN.md)。

## 阶段 D — 冒烟

阶段 A、B 完成后执行 [`docs/smoke-checklist.md`](./smoke-checklist.zh-CN.md)。

## 代理核对清单

- [ ] 发布 tarball 校验通过（HTTP 200，文件名含预期 sha）
- [ ] `init-env.sh` → `gen-secrets.sh`（幂等；`.env` 权限 600）
- [ ] 许可证与 LLM 由运维填写（非脚本生成）
- [ ] `preflight-env.sh` 通过（非生产才允许记录 `FLEET_SKIP_PREFLIGHT`）
- [ ] `fleet.sh up -d` 健康；`doctor.sh` 无关键异常
- [ ] 白标覆盖已应用；人设同步先 dry-run 再执行
- [ ] 冒烟清单完成
- [ ] 密钥未进入 git、聊天记录或日志

## 相关文档

- [`AGENTS.md`](../AGENTS.md) — 代理入口索引
- [`docs/operations/day-2-ops.md`](./operations/day-2-ops.zh-CN.md) — 升级与维护
