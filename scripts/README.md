# Scripts

## Brand preview and validation

| Script | Purpose |
|--------|---------|
| [`validate-artifacts.sh`](./validate-artifacts.sh) | Repo file presence, JSON parse, persona sanity, then [`validate-branding.py`](./validate-branding.py) |
| [`validate-branding.py`](./validate-branding.py) | Branding/theme/asset/contrast/persona rules (no network) |
| [`preview-login.py`](./preview-login.py) | Write static inert login HTML under `artifacts/brand-preview/` |
| [`capture-preview-screenshots.py`](./capture-preview-screenshots.py) | Playwright PNGs (1280×800 desktop, 390×844 mobile) |

Configurable validation ceilings: [`brand_validation_limits.json`](./brand_validation_limits.json).

### Quickstart

```bash
./scripts/validate-artifacts.sh
python3 scripts/preview-login.py
# optional screenshots:
pip install -r scripts/requirements-dev.txt && python -m playwright install chromium
python3 scripts/capture-preview-screenshots.py
```

### Tests

```bash
pip install -r scripts/requirements-dev.txt
PYTHONPATH=scripts pytest tests/ -q
```

### License / fidelity

The preview is a **customer-owned, approximate** renderer built from this repo's JSON and assets. It does not bundle chatkit-web AuthShell source. WCAG checks apply only to selected theme token pairs documented in the validator — not the full login UI.
