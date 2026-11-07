# Persona pack pin

How to pin your `persona-templates.json` and run a one-shot **replace** so the persona picker shows only your pack.

## Classic vs white-label

| | Default stack | White-label (this repo) |
|---|---------------|-------------------------|
| Pack JSON | Bundled default in chart/image | **This repo** → mount / ConfigMap |
| `PERSONA_TEMPLATE_CONFIG_PATH` | Unset (bundled) | **Always set** to mounted pack path |
| Boot `seedTemplates` | `upsert` / `insert_missing` | Same — **never** `replace_platform` on boot |
| One-shot prune | Do **not** run `replace_platform` | Run when pack changes or on first white-label deploy |

If you run prune once but boot still sees the full default catalog, the next restart can re-import extra roles. **Pin is mandatory** for white-label.

## Pin vs prune

| Mechanism | When | What it does |
|-----------|------|--------------|
| **Pin** (`PERSONA_TEMPLATE_CONFIG_PATH`) | Always on `persona-service` | Every boot seeds from your pack file (upsert) |
| **Prune Job / compose profile** | Once per pack version (or after pack edits) | `replace_platform`: upsert pack slugs, delete orphan **platform** templates |

## Safe workflow

1. Set `PERSONA_TEMPLATE_CONFIG_PATH` to the mounted path (see `deploy/compose/` or `deploy/helm/`).
2. **Dry-run first** — pass `--dry-run` to the sync CLI (Compose `persona-templates-sync` or Helm `personaTemplateSyncJob.extraArgs`).
3. Apply with `replace_platform` using the **same path** as the pin.
4. Confirm the picker shows only your templates; default should match `is_default: true` in your JSON (e.g. **General**).

## Sync binary (offline release only)

The tool ships **inside the chatkit / FinHub offline release**, not in this repo:

```text
/app/bin/sync-platform-persona-templates
```

Your pack file must set `"sync_mode": "replace_platform"`. Compose and Helm wrappers invoke this binary; follow your release README for service names and profiles.

### Bundled-path guard

The CLI refuses `replace_platform` when the resolved config is the **bundled** default `config/persona-templates.json` unless you pass **`--i-know`**. White-label deploys must use an **external** path (this repo's `persona-templates.json`). Never run replace against the bundled default on a shared multi-tenant default deploy.

## Database safety

- Prune scope: platform templates where `tenantId IS NULL` only.
- Agent foreign keys use **`onDelete: SetNull`** — removing an unused platform template does not delete agents; `templateId` becomes null.
