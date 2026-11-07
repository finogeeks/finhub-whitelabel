[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

Product page: [FinHub on finaios.ai](https://finaios.ai/en/products/finhub/)

# FinHub white-label customer template

Public template for forking or cloning when you deploy your own **FinHub** instance. Customize branding and persona packs in this repo, then point a deploy agent at your offline release tarball and this tree.

**FinHub** is the customer-facing product name. Upstream offline releases may still use `chatkit` in image or compose names — that is expected.

## Quick start

1. **Prereqs** — Docker Engine + Compose v2 (or Kubernetes + Helm); an offline FinHub/chatkit release tarball URL from your vendor; admin credentials for platform-settings seeding when the stack is up.
2. **Clone** — `git clone https://github.com/finogeeks/finhub-whitelabel` (or use this repo as a GitHub template).
3. **Customize** — see [`docs/customize.md`](./docs/customize.md).
   - Product copy + auth chrome → [`branding/platform-settings.json`](./branding/platform-settings.json)
   - Logos → [`branding/assets/`](./branding/assets/)
   - Persona starter pack → [`persona-templates.json`](./persona-templates.json)
   - Host / TLS → [`deploy/compose/`](./deploy/compose/) or [`deploy/helm/`](./deploy/helm/)
4. **Validate** — `./scripts/validate-artifacts.sh` (no network).
5. **Deploy** — give an agent the release URL, path to this fork, and credentials. Load [`skills/finhub-deploy/SKILL.md`](./skills/finhub-deploy/SKILL.md) and follow Phase 1 → Phase 2 (Phase 1.5 OAuth only if you need it).
6. **Smoke** — [`docs/smoke-checklist.md`](./docs/smoke-checklist.md).

## Repository layout

```
README.md
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
  persona-pack-pin.md
  customize.md
  smoke-checklist.md
skills/
  finhub-deploy/SKILL.md       # primary agent entrypoint
scripts/
  validate-artifacts.sh        # Soft P0: presence + JSON parse
```

## Reference deploy

A finished FinHub skin is live at [finhub.finaios.ai](https://finhub.finaios.ai) (Finogeeks reference — not a required hostname for your fork). Product page: FinHub on finaios.ai when published.

## Pack sync (summary)

Persona **replace** uses `/app/bin/sync-platform-persona-templates` inside the **offline release** image — not reimplemented in this repo. Pin `PERSONA_TEMPLATE_CONFIG_PATH` to your mounted `persona-templates.json`, then run the compose profile or Helm Job documented in [`docs/persona-pack-pin.md`](./docs/persona-pack-pin.md).

## What this repo does not contain

- No FinHub-named patches inside chatkit-web or chatkit-middleware
- No required `finhub.finaios.ai` host defaults in deploy config
- No application source — seeds, mounts, and deploy overlays only

## Support path

Customize artifacts here → agent runs `skills/finhub-deploy` with your release URL → smoke checklist. OAuth and advanced embed RP wiring are opt-in ([`deploy/oauth-provider.env.example`](./deploy/oauth-provider.env.example)).
