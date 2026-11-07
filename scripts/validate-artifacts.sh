#!/usr/bin/env bash
# Soft P0: required files present; JSON parse for platform-settings + persona pack.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REQUIRED=(
  README.md
  branding/platform-settings.json
  branding/theme-tokens.json
  branding/README.md
  branding/assets/acme-mark.svg
  branding/assets/acme-wordmark.svg
  branding/assets/favicon.svg
  branding/assets/og-acme.svg
  persona-templates.json
  deploy/compose/docker-compose.whitelabel.override.yml
  deploy/helm/values-whitelabel.yaml
  deploy/oauth-provider.env.example
  docs/persona-pack-pin.md
  docs/customize.md
  docs/smoke-checklist.md
  skills/finhub-deploy/SKILL.md
)

missing=0
for f in "${REQUIRED[@]}"; do
  if [[ ! -e "$f" ]]; then
    echo "MISSING: $f" >&2
    missing=1
  fi
done

if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import json, sys
from pathlib import Path
root = Path(".")
for rel in ("branding/platform-settings.json", "persona-templates.json", "branding/theme-tokens.json"):
    p = root / rel
    try:
        json.loads(p.read_text())
    except Exception as e:
        print(f"INVALID JSON: {rel}: {e}", file=sys.stderr)
        sys.exit(1)
# persona pack sanity
pack = json.loads((root / "persona-templates.json").read_text())
assert pack.get("sync_mode") == "replace_platform", "persona-templates.json: sync_mode must be replace_platform"
templates = pack.get("templates") or []
assert templates, "persona-templates.json: templates must be non-empty"
defaults = [t for t in templates if t.get("is_default")]
assert len(defaults) == 1, "persona-templates.json: exactly one is_default template"
print("JSON OK:", "branding/platform-settings.json", "persona-templates.json", "branding/theme-tokens.json")
PY
else
  echo "WARN: python3 not found; skipping JSON parse" >&2
fi

if [[ "$missing" -ne 0 ]]; then
  echo "validate-artifacts: FAIL (missing files)" >&2
  exit 1
fi

echo "validate-artifacts: PASS"
exit 0
