[English](./brand-preview.md)

# Brand preview (approximate)

Static login preview for white-label branding **before** deploy. Not a substitute for the live FinHub login page.

## Generate

```bash
python3 scripts/preview-login.py
python3 scripts/capture-preview-screenshots.py   # after Playwright install — see scripts/README.md
```

Artifacts land in `artifacts/brand-preview/`:

- `login-preview-en.html`
- `login-preview-desktop.png`
- `login-preview-mobile.png`

Every preview shows: **Approximate brand preview — compare with deployed login screen**.

## Post-deploy screenshot comparison

1. Deploy with Phase 2 overlays ([`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md)).
2. Open your public login URL in a browser (desktop width ~1280px, mobile ~390px).
3. Capture screenshots (browser devtools device mode is fine).
4. Compare with the local PNGs:
   - Product name and logo visible
   - `login_hero` title/subtitle on the hero side (layout may differ on live site)
   - `auth_login` title/subtitle near the form
   - Theme colors roughly match `branding/theme-tokens.json`
5. Log differences: upstream AuthShell layout, fonts, motion, marquee (`auth_show_marquee`), or fields your release does not expose yet.

**Authoritative UI:** deployed login. Preview is for early copy/theme/asset review only.

Agent skill: [`skills/finhub-brand/SKILL.md`](../skills/finhub-brand/SKILL.md).
