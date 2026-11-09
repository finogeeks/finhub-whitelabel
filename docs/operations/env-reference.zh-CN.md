[English](./env-reference.md) | [简体中文](./env-reference.zh-CN.md) | [繁體中文](./env-reference.zh-TW.md)

# 环境变量参考

发布包提供 `.env.example`。经 `init-env.sh` 复制为 `.env`。**切勿**将真实取值提交到 git 或贴在工单里。

图例：**自动** = `gen-secrets.sh` 或 `init-env.sh` 在占位/空值时填充；**人工** = 运维或供应商；**机密** = 按凭据保管；**可选** = 预检不要求必填。

## 引导流程

| 步骤 | 脚本 | 作用 |
|------|------|------|
| 1 | `init-env.sh` | `.env`、JWT PEM 文件、缺失时的 A2A 密钥、舰队 URL 修正 |
| 2 | `gen-secrets.sh` | `.env` 中的机器密钥 |
| 3 | 运维 | 许可证、LLM、registry、公网 URL |
| 4 | `preflight-env.sh` | 仍有占位符或许可证缺失则失败 |

## 自动生成（`gen-secrets.sh`）

仅在值为空、已知开发占位符或长度不足时替换（规则见发布包 `env-secrets.ts`）：

| 变量 | 机密 | 说明 |
|----------|--------|-------|
| `VERIFY_CODE_SECRET` | 是 | 至少 32 字节 |
| `INTERNAL_SERVICE_TOKEN` | 是 | 与舰队内部 API 共用；finops-staff 访问 claw-fleet-manager |
| `OPEN_LOOP_WAKE_JWT_SECRET` | 是 | 至少 32 字符 |
| `FINSAFE_AUTH_TOKEN` | 是 | |
| `USER_SECRETS_KEK` | 是 | base64 32 字节 KEK |
| `OIDC_STATE_COOKIE_SECRET` | 是 | |
| `SESSION_COOKIE_SECRET` | 是 | |
| `INTERNAL_APPROVAL_RESOLVE_TOKEN` | 是 | 空则生成 |
| `AI_INFRA_RS_CRON_INTERNAL_TOKEN` | 是 | 空则镜像 `INTERNAL_SERVICE_TOKEN` |
| `SERVICE_API_KEYS` | 是 | 替换开发占位映射 |
| `A2A_DELEGATION_SIGNING_KEY` | 是 | `init-env.sh` / `fleet.sh` 亦会保证（≥32 字节；已有则保留） |
| `FINOPS_STAFF_GENERIC_WEBHOOK_HMAC_SECRET` | 是 | 仅当 `.env` 中存在该键且值为空 |

**可选 finops 令牌**（仅当 `.env` 中**存在**该键时生成，含取消注释的 `KEY=` 存根）：

| 变量 | 机密 |
|----------|--------|
| `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` | 是 |
| `FINOPS_STAFF_INTERNAL_API_TOKEN` | 是 |
| `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` | 是 |

`gen-secrets` 完成后标准输出可能列出 `Optional finops filled: …`（**仅名称**）。

## 自动生成（`init-env.sh`，非 gen-secrets）

| 项 | 机密 | 说明 |
|------|--------|-------|
| `JWT_PRIVATE_KEY`、`JWT_PUBLIC_KEY`、`IDP_PUBLIC_KEY` | 是 | 自 `identity-service/keys/` PEM 写入 `.env` |
| Hermes 默认项 | 否 | 如缺失时 `FINSAFE_SKIP_LOCAL_SERVER=0`、`HERMES_EXECUTION_POSTURE=confined` |

## 必须人工

| 变量 | 机密 | 说明 |
|----------|--------|-------|
| `DEPLOYMENT_LICENSE_KEY` | 是 | **仅供应商** — 不生成 |
| `DEPLOYMENT_LICENSE_CIPHER` | 是 | **仅供应商** — 不生成 |

许可证缺失或无效 → identity-service 拒绝启动。

## 生产常见（人工）

| 变量 | 机密 | 预检 |
|----------|--------|-----------|
| `LLM_API_KEY` | 是 | 允许为空（真实推理需填写） |
| `CHATKIT_REGISTRY`、`CHATKIT_VERSION` | 否 | 拉取镜像 |
| `APP_URL`、Cookie 域 | 否 | 浏览器公网 URL |
| `ADMIN_EMAILS` | 否 | 初始管理员 |

## 可选人工（集成）

| 变量 | 机密 | 场景 |
|----------|--------|------|
| `TURNSTILE_SECRET`、`TURNSTILE_HOSTNAMES`、`TURNSTILE_SITEKEY` | 是（密钥） | 公网注册 |
| `FINOPS_STAFF_SLACK_WEBHOOK_URL` | 是 | Slack 通知 |
| `FINOPS_STAFF_NOTIFY_MIN_SEVERITY` | 否 | 通知门槛：`info`、`warning` 或 `critical`（默认 `warning`；无效或空 → `warning`）— 见 [finops-notifications](./finops-notifications.zh-CN.md) |
| 各通道 URL/密码 | 是 | 见 [finops-notifications](./finops-notifications.zh-CN.md) — 除上文 HMAC 外不由 gen-secrets 生成 |

## finops-staff 文档默认（客户姿态）

启用 finops-staff 时建议在 `.env` 保持：

```bash
FINOPS_STAFF_POLICY_MODE=readonly
FINOPS_STAFF_AUTO_ACT_DISABLED=true
FINOPS_STAFF_CLOSED_LOOP_ENABLED=false
```

Compose 覆盖（`${FINOPS_STAFF_AUTO_ACT_DISABLED:-true}` / `${FINOPS_STAFF_CLOSED_LOOP_ENABLED:-false}`）与 Helm（`finopsStaff.autoActDisabled: true`、`finopsStaff.closedLoopEnabled: false`，除非覆盖否则始终写入 Pod env）均与上表一致。已在发布语义 `eaf6b93b` 核对。

## JWT 与许可证

- **JWT** — 磁盘 PEM + `.env`；轮换见发布包说明。
- **许可证** — 续期联系供应商；本包不提供许可证生成器。

完整存根列表：发布树 `.env.example` 第 11 节（finops）。
