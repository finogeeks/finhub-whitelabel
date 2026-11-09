[English](./finops-notifications.md) | [简体中文](./finops-notifications.zh-CN.md) | [繁體中文](./finops-notifications.zh-TW.md)

# finops-staff 事件通知

外呼通知为**选配**。未配置通道时，finops-staff 仅做告警诊断，不访问外部系统。

## 通用行为

- 默认无任何外呼。
- 审批令牌与 Webhook URL **不会**出现在消息正文中。
- 单通道失败仅记日志；**不会**导致诊断失败（诊断成功时 `POST /webhooks/alertmanager` 仍为 `200`）。
- 负载 schema：`finops-incident-notify/v1`（通用 Webhook 原样 POST 该 JSON）。
- 每通道 HTTP 超时：`FINOPS_STAFF_NOTIFY_TIMEOUT_MS`（默认 `10000`）。

## 启用通道

逗号分隔列表：

```bash
FINOPS_STAFF_NOTIFY_CHANNELS=slack,feishu,email,generic
```

**兼容行为：** 未设置 `FINOPS_STAFF_NOTIFY_CHANNELS` 时，仅当配置了 `FINOPS_STAFF_SLACK_WEBHOOK_URL` 仍发 Slack；否则无外呼。

列表中的通道若缺少必填 env → 启动/doctor **警告**，跳过该通道。

## Slack

| 变量 | 必填 | 机密 |
|----------|----------|--------|
| `FINOPS_STAFF_SLACK_WEBHOOK_URL` | 是 | 是 — Incoming Webhook URL |

Incoming Webhook（blocks + text），无签名校验。不由 `gen-secrets.sh` 生成。

## 飞书 / Lark

别名：`feishu`、`lark`

| 变量 | 必填 | 机密 |
|----------|----------|--------|
| `FINOPS_STAFF_FEISHU_WEBHOOK_URL` | 是 | 是 |
| `FINOPS_STAFF_FEISHU_SIGNING_SECRET` | 否 | 是 — 自定义机器人 JSON 体 `timestamp` + `sign` |

交互卡片（`msg_type: interactive`）。

## 邮件

别名：`email`、`mail`

| 变量 | 默认 | 机密 |
|----------|---------|--------|
| `FINOPS_STAFF_SMTP_HOST` | — | 否 |
| `FINOPS_STAFF_SMTP_PORT` | `587` | 否 |
| `FINOPS_STAFF_SMTP_TLS` | 未设置 | 否 |
| `FINOPS_STAFF_SMTP_STARTTLS` | 587 且未强制 TLS 时为 `true` | 否 |
| `FINOPS_STAFF_SMTP_USER` / `_PASSWORD` | — | 是 |
| `FINOPS_STAFF_SMTP_FROM` | — | 否 |
| `FINOPS_STAFF_NOTIFY_EMAIL_TO` | 逗号分隔 | 否 |

纯文本 + 简单 HTML；SMTP AUTH。镜像内置 nodemailer（可离线）。地址/密码由运维提供。

## 通用 JSON Webhook

别名：`generic`、`webhook`

| 变量 | 必填 | 机密 |
|----------|----------|--------|
| `FINOPS_STAFF_GENERIC_WEBHOOK_URL` | 是 | 是 |
| `FINOPS_STAFF_GENERIC_WEBHOOK_TOKEN` | 否 | 是 — `Authorization: Bearer` |
| `FINOPS_STAFF_GENERIC_WEBHOOK_HMAC_SECRET` | 否 | 是 — `.env` 存在且为空时 `gen-secrets.sh` 可生成 |

### HMAC 校验（接收方示例）

设置 `FINOPS_STAFF_GENERIC_WEBHOOK_HMAC_SECRET` 后，请求带头：

```http
X-FinOps-Notify-Signature: sha256=<hex>
```

`<hex>` 为对**原始请求体**做 HMAC-SHA256 的十六进制摘要。

Node.js 校验片段：

```javascript
const crypto = require('crypto');

function verifyFinOpsNotify(req, secret) {
  const header = req.headers['x-finops-notify-signature'] || '';
  const match = /^sha256=([a-f0-9]+)$/i.exec(header);
  if (!match) return false;
  const expected = match[1].toLowerCase();
  const hmac = crypto.createHmac('sha256', secret).update(req.rawBody).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(hmac));
}
```

`gen-secrets.sh` 生成 HMAC 后请通过安全渠道分发给接收方（勿记录取值）。

## 钉钉

别名：`dingtalk`、`dingding`

| 变量 | 必填 | 机密 |
|----------|----------|--------|
| `FINOPS_STAFF_DINGTALK_WEBHOOK_URL` | 是 | 是 |
| `FINOPS_STAFF_DINGTALK_SIGNING_SECRET` | 否 | 是 — 追加 `&timestamp=<ms>&sign=<urlencoded base64 HmacSHA256>` |
| `FINOPS_STAFF_DINGTALK_KEYWORD` | 否 | 否 — 关键词安全机器人前缀 |

Markdown（`msgtype markdown`）。

## 企业微信（群机器人）

别名：`wecom`、`wechatwork`、`wxwork`

| 变量 | 必填 | 机密 |
|----------|----------|--------|
| `FINOPS_STAFF_WECOM_WEBHOOK_URL` | 是 | 是 — URL 内含 `key`，整段 URL 按机密保管 |

Markdown 内容截断至 4096 UTF-8 字节并附脚注说明。

## 审批通知

人工审批使用 `POST /webhooks/approval` 与头 `x-finops-approval-token`（若配置）及字段 `decision_id`，与上文 fan-out 通道无关。

## 相关

- [finops-staff](./finops-staff.zh-CN.md) · [环境参考](./env-reference.zh-CN.md)
