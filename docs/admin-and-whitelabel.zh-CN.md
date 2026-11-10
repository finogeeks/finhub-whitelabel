[English](./admin-and-whitelabel.md) | [简体中文](./admin-and-whitelabel.zh-CN.md) | [繁體中文](./admin-and-whitelabel.zh-TW.md)

# 管理端与白标仓库的边界

FinHub 管理端已经可以改 Logo、文案，并拉取预置技能。本仓库不替代这些页面。它只种子**人设模板**，以及品牌里**两个字段的首次文案**。只有这份额文案和界面写的是同一条配置。

对照实现：identity-service `PUT /admin/config/platform-settings`，skill-service `POST /admin/skills/sync-preset`。

## 不会互相覆盖的部分

| 管理端操作 | 写入位置 | 本仓库 |
| --- | --- | --- |
| **同步预置技能**（技能目录） | skill-service 的 catalog 卷和平台技能行 | 不挂 catalog，不调用 sync-preset，也不隐藏技能 |
| **人设包**固定 + 一次性 `replace_platform` | 仅平台人设模板（`tenantId` 为空） | `persona-templates.json` |
| **上传 / 移除 Logo** | `platform_settings.logo_url`，路径为 `/platform-uploads/...` | 设置 PUT **不会**写入种子里的 `logo_url` |
| **改产品名和登录主文案** | 同一条 `platform_settings` | 种子 PUT **会写入这两项**，并覆盖之后在界面里保存的文案 |

预置技能同步和白标部署谁先谁后都可以。再次同步技能不会重置品牌或人设包。人设修剪不会安装、隐藏或删除技能。

Compose profile 名 `persona-skill` 是发布包里的**人设**栈，不是 `POST /admin/skills/sync-preset`。

离线目录：管理端按钮下载的是发布包里的 `catalog_seed` 地址（或你们的内网镜像）。这是网络和发布包的事，本仓库不改这个 URL。

## 品牌：一条配置，两个写入方

运行时以 identity 的 `site_config` 键 `platform_settings` 为准，在**管理端 → 平台设置**里修改。

`PUT /admin/config/platform-settings` 只接受：

- `product_name.zh` / `product_name.en`
- `login_hero.title` 与 `login_hero.subtitle`（中英）

处理时保留当前的 `logo_url`。浏览器标题由**中文产品名**派生（`{名称}管理后台`、`{名称}智能助手`），管理端没有单独的标题字段。

下列键仍留在 [`branding/platform-settings.json`](../branding/platform-settings.json) 里，给 `./scripts/validate-artifacts.sh` 和静态登录预览用。线上 PUT **会丢掉**它们：

| 种子字段 | 线上效果 |
| --- | --- |
| `product_name`、`login_hero` | 会写入。之后再跑种子 PUT，会换成 Git 里的文案。 |
| `logo_url` | 忽略。登录标只在**上传 Logo** 或**移除 Logo** 之后改变。 |
| `document_titles` | 忽略。标题跟着中文产品名走。 |
| `auth_login`、`auth_register`、`family_line`、`auth_show_marquee` | 忽略。登录页用的是 `login_hero`，不用这些表单标题和页脚。 |

把 [`branding/assets/`](../branding/assets/) 挂到 `/static/branding` 不会因此改登录 Logo。Phase 2 之后，若启动页要显示你们的图，到管理端上传。再次执行种子 PUT 不会清掉已上传的 Logo。

[`branding/theme-tokens.json`](../branding/theme-tokens.json) 仍只是设计参照（`_consumed_by_chatkit: false`）。

## 建议怎么用

1. **首次安装** — Phase 2 可以 PUT 种子，让产品名和登录主文案与 fork 一致。然后在管理端上传 Logo。
2. **上线后改文案或 Logo** — 用**平台设置**。除非就是要把界面文案换回 Git 文件，否则不要再跑种子 PUT。
3. **以 Git 为文案来源** — 改 `product_name` 和 `login_hero` 后再 PUT，并接受管理端文案被替换。只有在界面里移除过 Logo 时才需要重传。
4. **预置技能** — 目录 pin 要刷新时，用**同步预置技能**。不要指望 `persona-templates.json` 改变技能市场。
5. **人设** — 固定和一次性 replace 仍按 [`persona-pack-pin.zh-CN.md`](./persona-pack-pin.zh-CN.md)。人设选择器不是技能目录。
