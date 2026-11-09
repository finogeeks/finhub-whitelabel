[English](./finops-notifications.md) | [简体中文](./finops-notifications.zh-CN.md) | [繁體中文](./finops-notifications.zh-TW.md)

# finops-staff 事件通知

外呼通知為**選配**。未設定通道時，finops-staff 僅做告警診斷，不存取外部系統。

## 通用行為

- 預設無任何外呼。
- 核准權杖與 Webhook URL **不會**出現在訊息正文中。
- 單一通道失敗僅記錄日誌；**不會**導致診斷失敗（診斷成功時 `POST /webhooks/alertmanager` 仍為 `200`）。
- 負載 schema：`finops-incident-notify/v1`（通用 Webhook 原樣 POST 該 JSON）。
- 每通道 HTTP 逾時：`FINOPS_STAFF_NOTIFY_TIMEOUT_MS`（預設 `10000`）。

## 啟用通道

逗號分隔清單：

```bash
FINOPS_STAFF_NOTIFY_CHANNELS=slack,feishu,email,generic
```

**相容行為：** 未設定 `FINOPS_STAFF_NOTIFY_CHANNELS` 時，僅當設定了 `FINOPS_STAFF_SLACK_WEBHOOK_URL` 仍送 Slack；否則不外呼。

清單中的通道若缺少必填 env → 啟動/doctor **警告**，略過該通道。

## Slack

| 變數 | 必填 | 機密 |
|----------|----------|--------|
| `FINOPS_STAFF_SLACK_WEBHOOK_URL` | 是 | 是 — Incoming Webhook URL |

Incoming Webhook（blocks + text），無簽章驗證。不由 `gen-secrets.sh` 產生。

## 飛書 / Lark

別名：`feishu`、`lark`

| 變數 | 必填 | 機密 |
|----------|----------|--------|
| `FINOPS_STAFF_FEISHU_WEBHOOK_URL` | 是 | 是 |
| `FINOPS_STAFF_FEISHU_SIGNING_SECRET` | 否 | 是 — 自訂機器人 JSON 本體 `timestamp` + `sign` |

互動卡片（`msg_type: interactive`）。

## 郵件

別名：`email`、`mail`

| 變數 | 預設 | 機密 |
|----------|---------|--------|
| `FINOPS_STAFF_SMTP_HOST` | — | 否 |
| `FINOPS_STAFF_SMTP_PORT` | `587` | 否 |
| `FINOPS_STAFF_SMTP_TLS` | 未設定 | 否 |
| `FINOPS_STAFF_SMTP_STARTTLS` | 587 且未強制 TLS 時為 `true` | 否 |
| `FINOPS_STAFF_SMTP_USER` / `_PASSWORD` | — | 是 |
| `FINOPS_STAFF_SMTP_FROM` | — | 否 |
| `FINOPS_STAFF_NOTIFY_EMAIL_TO` | 逗號分隔 | 否 |

純文字 + 簡單 HTML；SMTP AUTH。映像內建 nodemailer（可離線）。位址/密碼由維運提供。

## 通用 JSON Webhook

別名：`generic`、`webhook`

| 變數 | 必填 | 機密 |
|----------|----------|--------|
| `FINOPS_STAFF_GENERIC_WEBHOOK_URL` | 是 | 是 |
| `FINOPS_STAFF_GENERIC_WEBHOOK_TOKEN` | 否 | 是 — `Authorization: Bearer` |
| `FINOPS_STAFF_GENERIC_WEBHOOK_HMAC_SECRET` | 否 | 是 — `.env` 存在且為空時 `gen-secrets.sh` 可產生 |

### HMAC 驗證（接收方範例）

設定 `FINOPS_STAFF_GENERIC_WEBHOOK_HMAC_SECRET` 後，請求帶標頭：

```http
X-FinOps-Notify-Signature: sha256=<hex>
```

`<hex>` 為對**原始請求本體**做 HMAC-SHA256 的十六進位摘要。

Node.js 驗證片段：

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

`gen-secrets.sh` 產生 HMAC 後請透過安全管道分發給接收方（勿記錄取值）。

## 釘釘

別名：`dingtalk`、`dingding`

| 變數 | 必填 | 機密 |
|----------|----------|--------|
| `FINOPS_STAFF_DINGTALK_WEBHOOK_URL` | 是 | 是 |
| `FINOPS_STAFF_DINGTALK_SIGNING_SECRET` | 否 | 是 — 附加 `&timestamp=<ms>&sign=<urlencoded base64 HmacSHA256>` |
| `FINOPS_STAFF_DINGTALK_KEYWORD` | 否 | 否 — 關鍵字安全機器人前綴 |

Markdown（`msgtype markdown`）。

## 企業微信（群機器人）

別名：`wecom`、`wechatwork`、`wxwork`

| 變數 | 必填 | 機密 |
|----------|----------|--------|
| `FINOPS_STAFF_WECOM_WEBHOOK_URL` | 是 | 是 — URL 內含 `key`，整段 URL 依機密封存 |

Markdown 內容截斷至 4096 UTF-8 位元組並附註腳說明。

## 核准通知

人工核准使用 `POST /webhooks/approval` 與標頭 `x-finops-approval-token`（若設定）及欄位 `decision_id`，與上文 fan-out 通道無關。

## 相關

- [finops-staff](./finops-staff.zh-TW.md) · [環境參考](./env-reference.zh-TW.md)
