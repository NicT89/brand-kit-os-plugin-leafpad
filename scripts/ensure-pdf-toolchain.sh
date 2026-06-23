#!/usr/bin/env bash
# Ensure a working pure-Python PDF toolchain for generating documents (e.g. the
# partnership proposal) in remote/web sessions.
#
# Why this exists: this repo's containers ship LibreOffice *core* only (no
# libreoffice-writer), so `soffice --convert-to pdf file.html` fails with
# "source file could not be loaded" — HTML import is a Writer-module filter that
# isn't installed. The reliable, dependency-light path is fpdf2, but the system
# `cryptography` rust binding can be broken (missing _cffi_backend), which fpdf2
# imports. This script fixes cffi and ensures fpdf2 imports. Idempotent; fast
# when already healthy; never fails the session.

set -u

log() { printf '[pdf-toolchain] %s\n' "$1"; }

# Already healthy? Do nothing.
if python3 -c "import fpdf" >/dev/null 2>&1; then
  log "fpdf2 OK"
  exit 0
fi

log "fpdf2 not importable — provisioning"

# The usual culprit: cryptography's rust binding can't find _cffi_backend.
if ! python3 -c "import _cffi_backend" >/dev/null 2>&1; then
  log "reinstalling cffi"
  pip install --force-reinstall --no-cache-dir --quiet cffi >/dev/null 2>&1 || \
    log "cffi reinstall failed (continuing)"
fi

log "installing fpdf2"
pip install --quiet fpdf2 >/dev/null 2>&1 || log "fpdf2 install failed"

if python3 -c "import fpdf" >/dev/null 2>&1; then
  log "fpdf2 ready"
else
  log "WARNING: fpdf2 still not importable; PDF generation may be unavailable"
fi

exit 0
