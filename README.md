[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# FinHub white-label customer template

## What is FinHub

**The control center for your company's AI agents.** FinHub lets your IT team control who can use which AI agents and tools, and keeps an uneditable record of every conversation. It runs on your own servers, with our agent engine (FinClaw) or your own.

Learn more on the [FinHub product page at finaios.ai](https://finaios.ai/en/products/finhub/).

Public template for forking or cloning when you deploy your own **FinHub** instance. Customize branding and persona packs in this repo, then point a deploy agent at your offline release tarball and this tree.

**FinHub** is the customer-facing product name. Upstream offline releases may still use `chatkit` in image or compose names — that is expected.

**Coding agents** — start at [`AGENTS.md`](./AGENTS.md) (skill order, tarball dependency, secret rules). Human-readable deploy flow: [`docs/agent-deploy-runbook.md`](./docs/agent-deploy-runbook.md).

## Quick start

1. **Prereqs** — Docker Engine + Compose v2 (or Kubernetes + Helm); an offline FinHub/chatkit release tarball URL from your vendor; deployment license + LLM keys per release `.env.example`; admin credentials for platform-settings seeding when the stack is up.
2. **Clone** — `git clone https://github.com/finogeeks/finhub-whitelabel` (or use this repo as a GitHub template).
3. **Customize** — see [`docs/customize.md`](./docs/customize.md).
   - Product copy + auth chrome → [`branding/platform-settings.json`](./branding/platform-settings.json)
   - Logos → [`branding/assets/`](./branding/assets/)
   - Persona starter pack → [`persona-templates.json`](./persona-templates.json)
   - Host / TLS → [`deploy/compose/`](./deploy/compose/) or [`deploy/helm/`](./deploy/helm/)
4. **Validate & preview** — `./scripts/validate-artifacts.sh` (no network); optional brand preview via [`skills/finhub-brand/SKILL.md`](./skills/finhub-brand/SKILL.md).
5. **Deploy** — give an agent the release URL, path to this fork, and credentials. Load [`skills/finhub-deploy/SKILL.md`](./skills/finhub-deploy/SKILL.md): tarball verify → `init-env.sh` → `gen-secrets.sh` → license + `LLM_API_KEY` → `preflight-env.sh` → `fleet.sh up -d` → `doctor.sh` (from the **release bundle** when present) → Phase 2 overlays (Phase 1.5 OAuth or finops-staff only if you need them).
6. **Smoke** — [`docs/smoke-checklist.md`](./docs/smoke-checklist.md) (include login, chat, streamed reply).

## Repository layout

```
README.md
AGENTS.md                      # coding agent entry (skills + tarball dependency)
branding/
  platform-settings.json       # Option B auth / product chrome seed
  theme-tokens.json            # design SoT only (_consumed_by_chatkit: false)
  assets/                      # your mark, wordmark, favicon, OG
  README.md
persona-templates.json         # starter pack (pin + one-shot replace)
deploy/
  compose/                     # mounts, PERSONA_TEMPLATE_CONFIG_PATH, sync profile
  helm/                        # values + ConfigMap stubs
  oauth-provider.env.example   # opt-in OAuth only
docs/
  agent-deploy-runbook.md      # zero-to-running (en / zh-CN / zh-TW)
  operations/
    install.md                 # init-env → fleet → doctor
    env-reference.md           # auto-generated vs human-supplied secrets
    finops-staff.md            # optional supervised self-heal
    finops-notifications.md    # alert channels
    day-2-ops.md               # upgrade, backup, teardown
  persona-pack-pin.md
  customize.md
  smoke-checklist.md
  brand-preview.md             # post-deploy screenshot comparison
skills/
  finhub-deploy/SKILL.md       # primary agent entrypoint
  finhub-brand/SKILL.md        # brand validate + static login preview
scripts/
  validate-artifacts.sh        # presence + JSON + branding validator
  validate-branding.py
  preview-login.py
  capture-preview-screenshots.py
artifacts/
  brand-preview/               # generated preview HTML + PNGs (committed after generation)
```

## Reference deploy

A finished FinHub skin is live at [finhub.finaios.ai](https://finhub.finaios.ai) (Finogeeks reference — not a required hostname for your fork). Product page: [FinHub on finaios.ai](https://finaios.ai/en/products/finhub/).

## Pack sync (summary)

Persona **replace** uses `/app/bin/sync-platform-persona-templates` inside the **offline release** image — not reimplemented in this repo. Pin `PERSONA_TEMPLATE_CONFIG_PATH` to your mounted `persona-templates.json`, then run the compose profile or Helm Job documented in [`docs/persona-pack-pin.md`](./docs/persona-pack-pin.md).

## What this repo does not contain

- No FinHub-named patches inside chatkit-web or chatkit-middleware
- No required `finhub.finaios.ai` host defaults in deploy config
- No application source — seeds, mounts, and deploy overlays only
- No offline release images or bundle scripts (`init-env.sh`, `gen-secrets.sh`, `preflight-env.sh`, `fleet.sh`, `doctor.sh`) — those ship in the vendor tarball (see [`AGENTS.md`](./AGENTS.md))

## Support path

Customize artifacts here → bootstrap env in the release tree ([`docs/operations/install.md`](./docs/operations/install.md)) → agent runs `skills/finhub-deploy` with your release URL → smoke checklist. Optional finops-staff alerting is off by default ([`docs/operations/finops-staff.md`](./docs/operations/finops-staff.md)). OAuth and advanced embed RP wiring are opt-in ([`deploy/oauth-provider.env.example`](./deploy/oauth-provider.env.example)).
