[English](./admin-and-whitelabel.md) | [简体中文](./admin-and-whitelabel.zh-CN.md) | [繁體中文](./admin-and-whitelabel.zh-TW.md)

# Admin console vs this white-label repo

FinHub already lets an admin change logo and wording, and pull preset skills, from the admin UI. This repo does not replace those screens. It seeds **persona templates** and a **first-install copy** of two branding fields. The two paths share a store only for that copy.

Checked against identity-service `PUT /admin/config/platform-settings` and skill-service `POST /admin/skills/sync-preset`.

## What does not collide

| Admin action | Store | This repo |
| --- | --- | --- |
| **Sync preset skills** (skill catalog) | skill-service catalog volume + platform skill rows | Does not mount a catalog, does not call sync-preset, does not hide skills |
| **Persona pack** pin + one-shot `replace_platform` | Platform persona templates (`tenantId` null) only | `persona-templates.json` |
| **Upload / remove logo** | `platform_settings.logo_url` → `/platform-uploads/...` | Seed JSON `logo_url` is **not** written by the settings PUT |
| **Edit product name and login hero** | Same `platform_settings` row | Seed PUT **writes these two fields** and overwrites later admin edits |

Preset-skill sync and a white-label deploy can run in either order. Repeating skill sync does not reset branding or the persona pack. The persona prune does not install, hide, or delete skills.

The Compose profile name `persona-skill` is the release **persona** stack. It is not `POST /admin/skills/sync-preset`.

Offline catalogs: the admin button downloads the release `catalog_seed` URL (or your internal mirror). That is a network/release concern. This repo does not change that URL.

## Branding: one row, two writers

Runtime source of truth is identity `site_config` key `platform_settings`, edited under **Admin → Platform settings**.

`PUT /admin/config/platform-settings` accepts only:

- `product_name.zh` / `product_name.en`
- `login_hero.title` and `login_hero.subtitle` (zh/en)

The handler keeps the current `logo_url`. Browser titles are derived from the Chinese product name (`{name}管理后台`, `{name}智能助手`). They are not a separate admin field.

These keys stay in [`branding/platform-settings.json`](../branding/platform-settings.json) for `./scripts/validate-artifacts.sh` and the static login preview. The live PUT **drops** them:

| Seed key | Live effect |
| --- | --- |
| `product_name`, `login_hero` | Written. A later seed PUT replaces admin-saved copy. |
| `logo_url` | Ignored. Login mark changes only after **upload logo** or **remove logo**. |
| `document_titles` | Ignored. Titles follow the Chinese product name. |
| `auth_login`, `auth_register`, `family_line`, `auth_show_marquee` | Ignored. Login uses `login_hero`, not these form/footer keys. |

Mounting [`branding/assets/`](../branding/assets/) at `/static/branding` does not set the login logo. After Phase 2, set the mark in the admin UI if the splash must show your file. Re-running the seed PUT does not clear an uploaded logo.

[`branding/theme-tokens.json`](../branding/theme-tokens.json) stays a design reference (`_consumed_by_chatkit: false`).

## How to operate

1. **First install** — Phase 2 may PUT the seed so product name and login hero match the fork. Then upload the logo in admin.
2. **Day-2 copy or logo** — use **Platform settings**. Do not re-run the seed PUT unless you intend to replace the admin copy with the Git file.
3. **Git as source of copy** — edit `product_name` and `login_hero`, PUT again, and accept that the admin text is replaced. Re-upload the logo only if you removed it in the UI.
4. **Preset skills** — use **Sync preset skills** whenever the catalog pin should refresh. Do not expect `persona-templates.json` to change the skill market.
5. **Personas** — keep the pin and the one-shot replace in [`persona-pack-pin.md`](./persona-pack-pin.md). That picker is not the skill catalog.
