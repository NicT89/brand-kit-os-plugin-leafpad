#!/usr/bin/env python3
"""Enforce the plugin version-bump rule.

Run on pull_request. Fails when any plugin file changed versus the PR base but
the plugin version was not increased. Also enforces that the version is kept in
sync across plugin.json and marketplace.json, and that `author` is an object
(the schema requirement that broke the 1.4.3 marketplace install).
"""
import json
import os
import subprocess
import sys

PLUGIN_MANIFEST = "plugins/brand-kit-os-leafpad/.claude-plugin/plugin.json"
MARKETPLACE = ".claude-plugin/marketplace.json"
WATCH_PREFIXES = ("plugins/", ".claude-plugin/")


def fail(msg):
    print(f"::error::{msg}")
    sys.exit(1)


def parse_version(value):
    try:
        return tuple(int(p) for p in str(value).strip().split(".")[:3])
    except ValueError:
        fail(f"Unparseable version: {value!r}")


def load_head(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_at(ref, path):
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def changed_files(base):
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line for line in out.split("\n") if line.strip()]


def main():
    base = os.environ.get("BASE_SHA")
    if not base:
        fail("BASE_SHA env var not set")

    plugin = load_head(PLUGIN_MANIFEST)
    marketplace = load_head(MARKETPLACE)

    # 1. author must be an object (the exact schema bug that broke install).
    if not isinstance(plugin.get("author"), dict):
        fail("plugin.json `author` must be an object, e.g. { \"name\": ..., \"url\": ... }")

    # 2. version must be identical across the three places it appears.
    versions = {
        "plugin.json": plugin["version"],
        "marketplace.metadata": marketplace["metadata"]["version"],
        "marketplace.plugins[0]": marketplace["plugins"][0]["version"],
    }
    if len(set(versions.values())) != 1:
        fail(f"Version mismatch across manifests: {versions}. Keep them in sync.")

    # 3. require a bump when plugin-relevant files changed.
    relevant = [f for f in changed_files(base) if f.startswith(WATCH_PREFIXES)]
    if not relevant:
        print("No plugin files changed; version bump not required.")
        return

    base_plugin = load_at(base, PLUGIN_MANIFEST)
    if base_plugin is None:
        print("No base manifest found (new plugin); skipping bump comparison.")
        return

    base_v = parse_version(base_plugin["version"])
    head_v = parse_version(plugin["version"])
    if head_v <= base_v:
        fail(
            f"{len(relevant)} plugin file(s) changed but version was not bumped "
            f"(base={base_plugin['version']}, head={plugin['version']}). "
            f"Bump {PLUGIN_MANIFEST} and {MARKETPLACE}."
        )

    print(f"Version bumped {base_plugin['version']} -> {plugin['version']} "
          f"for {len(relevant)} changed plugin file(s). OK.")


if __name__ == "__main__":
    main()
