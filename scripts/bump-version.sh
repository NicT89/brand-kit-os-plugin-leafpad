#!/usr/bin/env bash
# Bump the plugin version everywhere CI expects it, in one step.
#
# Why this exists: the `version-bump` CI job (.github/scripts/check_version_bump.py)
# requires the version to be identical across THREE places:
#   1. plugins/brand-kit-os-leafpad/.claude-plugin/plugin.json  -> .version
#   2. .claude-plugin/marketplace.json                          -> .metadata.version
#   3. .claude-plugin/marketplace.json                          -> .plugins[0].version
# Bumping only plugin.json (easy to do by hand) fails CI with a version-mismatch
# error. This script updates all three at once so they never drift.
#
# Usage:
#   scripts/bump-version.sh 1.7.0
#
# It only rewrites the `version` value(s) in each manifest — no reformatting of
# the surrounding JSON — then verifies the three are in sync.

set -euo pipefail

PLUGIN_MANIFEST="plugins/brand-kit-os-leafpad/.claude-plugin/plugin.json"
MARKETPLACE=".claude-plugin/marketplace.json"

log() { printf '[bump-version] %s\n' "$1"; }
die() { printf '[bump-version] ERROR: %s\n' "$1" >&2; exit 1; }

NEW_VERSION="${1:-}"
[ -n "$NEW_VERSION" ] || die "usage: scripts/bump-version.sh <new-version>  (e.g. 1.7.0)"

# Validate semver X.Y.Z (the version-bump check parses exactly three integers).
if ! printf '%s' "$NEW_VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  die "version must be X.Y.Z with integer parts, got: $NEW_VERSION"
fi

# Run from the repo root so the relative manifest paths resolve.
cd "$(git rev-parse --show-toplevel)"

[ -f "$PLUGIN_MANIFEST" ] || die "not found: $PLUGIN_MANIFEST (run from the repo)"
[ -f "$MARKETPLACE" ]     || die "not found: $MARKETPLACE (run from the repo)"

NEW_VERSION="$NEW_VERSION" python3 - "$PLUGIN_MANIFEST" "$MARKETPLACE" <<'PY'
import json
import os
import re
import sys

new = os.environ["NEW_VERSION"]
plugin_path, marketplace_path = sys.argv[1], sys.argv[2]

# Rewrite only lines of the form  "version": "..."  — leaves every other key,
# comment, and whitespace byte-for-byte untouched (minimal diff, no reflow).
version_line = re.compile(r'("version"\s*:\s*")[^"]*(")')

def rewrite(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    updated, n = version_line.subn(rf"\g<1>{new}\g<2>", text)
    if n == 0:
        sys.exit(f"[bump-version] ERROR: no version field found in {path}")
    # Re-parse to guarantee we didn't corrupt the JSON.
    json.loads(updated)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(updated)
    return n

rewrite(plugin_path)
rewrite(marketplace_path)

# Verify the three canonical fields now match, exactly as CI checks them.
plugin = json.load(open(plugin_path, encoding="utf-8"))
mkt = json.load(open(marketplace_path, encoding="utf-8"))
seen = {
    "plugin.json .version": plugin["version"],
    "marketplace .metadata.version": mkt["metadata"]["version"],
    "marketplace .plugins[0].version": mkt["plugins"][0]["version"],
}
if len(set(seen.values())) != 1 or plugin["version"] != new:
    sys.exit(f"[bump-version] ERROR: versions did not sync: {seen}")
PY

log "Version set to $NEW_VERSION across plugin.json + marketplace.json (metadata + plugins[0])."
log "Next: add a CHANGELOG.md entry, then commit all changed files together."
