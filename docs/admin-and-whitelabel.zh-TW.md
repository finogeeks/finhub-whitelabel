[English](./admin-and-whitelabel.md) | [简体中文](./admin-and-whitelabel.zh-CN.md) | [繁體中文](./admin-and-whitelabel.zh-TW.md)

# 管理端與白標儲存庫的邊界

FinHub 管理端已經可以改 Logo、文案，並拉取預置技能。本儲存庫不取代這些頁面。它只種子**人設範本**，以及品牌裡**兩個欄位的首次文案**。只有這份文案和介面寫的是同一條設定。

對照實作：identity-service `PUT /admin/config/platform-settings`，skill-service `POST /admin/skills/sync-preset`。

## 不會互相覆蓋的部分

| 管理端操作 | 寫入位置 | 本儲存庫 |
| --- | --- | --- |
| **同步預置技能**（技能目錄） | skill-service 的 catalog 卷和平台技能列 | 不掛 catalog，不呼叫 sync-preset，也不隱藏技能 |
| **人設包**固定 + 一次性 `replace_platform` | 僅平台人設範本（`tenantId` 為空） | `persona-templates.json` |
| **上傳 / 移除 Logo** | `platform_settings.logo_url`，路徑為 `/platform-uploads/...` | 設定 PUT **不會**寫入種子裡的 `logo_url` |
| **改產品名和登入主文案** | 同一條 `platform_settings` | 種子 PUT **會寫入這兩項**，並覆蓋之後在介面裡儲存的文案 |

預置技能同步和白標部署誰先誰後都可以。再次同步技能不會重設品牌或人設包。人設修剪不會安裝、隱藏或刪除技能。

Compose profile 名 `persona-skill` 是發佈套件裡的**人設**堆疊，不是 `POST /admin/skills/sync-preset`。

離線目錄：管理端按鈕下載的是發佈套件裡的 `catalog_seed` 位址（或你們的內網鏡像）。這是網路和發佈套件的事，本儲存庫不改這個 URL。

## 品牌：一條設定，兩個寫入方

執行時以 identity 的 `site_config` 鍵 `platform_settings` 為準，在**管理端 → 平台設定**裡修改。

`PUT /admin/config/platform-settings` 只接受：

- `product_name.zh` / `product_name.en`
- `login_hero.title` 與 `login_hero.subtitle`（中英）

處理時保留目前的 `logo_url`。瀏覽器標題由**中文產品名**衍生（`{名稱}管理後台`、`{名稱}智能助手`），管理端沒有單獨的標題欄位。

下列鍵仍留在 [`branding/platform-settings.json`](../branding/platform-settings.json) 裡，給 `./scripts/validate-artifacts.sh` 和靜態登入預覽用。線上 PUT **會丟掉**它們：

| 種子欄位 | 線上效果 |
| --- | --- |
| `product_name`、`login_hero` | 會寫入。之後再跑種子 PUT，會換成 Git 裡的文案。 |
| `logo_url` | 忽略。登入標只在**上傳 Logo** 或**移除 Logo** 之後改變。 |
| `document_titles` | 忽略。標題跟著中文產品名走。 |
| `auth_login`、`auth_register`、`family_line`、`auth_show_marquee` | 忽略。登入頁用的是 `login_hero`，不用這些表單標題和頁尾。 |

把 [`branding/assets/`](../branding/assets/) 掛到 `/static/branding` 不會因此改登入 Logo。Phase 2 之後，若啟動頁要顯示你們的圖，到管理端上傳。再次執行種子 PUT 不會清掉已上傳的 Logo。

[`branding/theme-tokens.json`](../branding/theme-tokens.json) 仍只是設計參照（`_consumed_by_chatkit: false`）。

## 建議怎麼用

1. **首次安裝** — Phase 2 可以 PUT 種子，讓產品名和登入主文案與 fork 一致。然後在管理端上傳 Logo。
2. **上線後改文案或 Logo** — 用**平台設定**。除非就是要把介面文案換回 Git 檔案，否則不要再跑種子 PUT。
3. **以 Git 為文案來源** — 改 `product_name` 和 `login_hero` 後再 PUT，並接受管理端文案被替換。只有在介面裡移除過 Logo 時才需要重傳。
4. **預置技能** — 目錄 pin 要重新整理時，用**同步預置技能**。不要指望 `persona-templates.json` 改變技能市場。
5. **人設** — 固定和一次性 replace 仍按 [`persona-pack-pin.zh-TW.md`](./persona-pack-pin.zh-TW.md)。人設選擇器不是技能目錄。
