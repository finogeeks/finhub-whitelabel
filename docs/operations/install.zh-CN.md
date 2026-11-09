[English](./install.md) | [简体中文](./install.zh-CN.md) | [繁體中文](./install.zh-TW.md)

# 安装与首次启动

说明 FinHub 离线发布包中脚本的**默认本地部署路径**。脚本名称与顺序固定；compose 文件名可能因版本略有不同——若发布 README 指定其他文件，以其为准。

## 前置条件

- Docker + Compose v2、`openssl`、`bun`
- 供应商下发的部署许可证（`DEPLOYMENT_LICENSE_KEY`、`DEPLOYMENT_LICENSE_CIPHER`）
- 生产环境需配置 LLM 端点与 `LLM_API_KEY`（开发用 mock LLM 不能承载真实用户）

## 引导顺序

```bash
cd <release-root>   # 含 .env.example 与 scripts/ 的目录

./scripts/init-env.sh
./scripts/gen-secrets.sh
```

1. **`init-env.sh`** — 若无 `.env` 则从 `.env.example` 创建；补齐 Hermes/FinSAFE 舰队默认值；在 `services/platform/identity-service/keys/` 生成 **JWT PEM** 并写入 `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY` / `IDP_PUBLIC_KEY`；缺失时生成 A2A 委托密钥；许可证为空时提示。

2. **`gen-secrets.sh`** — 通过 `env-secrets-cli.ts` 幂等写入机器密钥；**不回显取值**；`.env` 设为 `600`。需要 `bun`。

**运维编辑 `.env`**（人工提供）：

- `DEPLOYMENT_LICENSE_KEY`、`DEPLOYMENT_LICENSE_CIPHER`
- `LLM_API_KEY`（及模型/提供商，如非默认）
- 非本地镜像时 `CHATKIT_REGISTRY` / `CHATKIT_VERSION`
- 对外访问的 `APP_URL` 等

```bash
./scripts/preflight-env.sh
```

若仍有占位符或许可证缺失，仅列出**变量名**。

离线包：

```bash
./scripts/load-images.sh
```

启动：

```bash
./scripts/fleet.sh up -d
```

`fleet.sh` 默认执行与上相同的预检（除非绕过），启动 compose 并按发布说明等待 identity/fleet-manager、协调租户 claw。

```bash
./scripts/doctor.sh
./scripts/doctor.sh --logs
```

## 本地部署：默认零外部依赖

- **Turnstile** — 可选。 air-gapped 注册请勿设置 `TURNSTILE_SECRET`、`TURNSTILE_HOSTNAMES`、`TURNSTILE_SITEKEY`。
- **finops-staff 通知** — 未配置前不发外呼（见 [finops-notifications](./finops-notifications.zh-CN.md)）。
- **Slack / 飞书等** — 对话能力不依赖外联。

## `FLEET_SKIP_PREFLIGHT`（仅非生产）

```bash
FLEET_SKIP_PREFLIGHT=1 ./scripts/fleet.sh up -d
```

会打印：

```text
⚠️  FLEET_SKIP_PREFLIGHT=... — skipping scripts/preflight-env.sh
    (dev/drill/dogfood only; production must run preflight + real license)
```

仅用于工程检出、演练包或内部 dogfood，且运维接受占位符/许可证风险。**客户生产环境禁止使用。**

## 启动之后

- 白标：[`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md)
- 冒烟：[`docs/smoke-checklist.md`](../smoke-checklist.zh-CN.md)
- 可选 FinOps：[finops-staff](./finops-staff.zh-CN.md)

## 冒烟（API）

发布树若有 `scripts/test-e2e-api.sh` 可执行；否则通过网关 URL（compose 文档中常见 `26100`）完成登录与对话验证。
