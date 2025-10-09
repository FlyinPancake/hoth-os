# Agent Guide for hoth-os

Build/lint/test:
- Build: `just build` (alias: `podman build .`); tag local: `podman build -t local/hoth-os:dev .`
- Lint: `just lint` (hadolint + actionlint); CI gates build on lint pass
- Tests: none configured

Structure:
- `rootfs/` → copied to `/` in image; `rootfs/usr/share/hoth-os/` has apps/, quadlets/, justfile
- Apps: self-contained in `apps/<name>/` with justfile (install/uninstall/status/logs recipes) + optional config/
- Build-time only: Containerfile, justfile, .github/, *.md docs

Code style:
- **Shell scripts**: `set -Eeuo pipefail` at start; quote vars; no heredocs in app justfiles
- **Containerfile**: group RUN steps with `&&`; pkgs: `dnf -y ... && dnf clean all && rm -rf /var/cache/dnf`; layer order: least→most changed
- **justfile**: `set shell := ["bash", "-Eeuo", "pipefail", "-c"]`; kebab-case names; idempotent; gum for wizards (apps only)
- **App justfiles**: echo settings after gum input; 4 recipes: install, uninstall, status, logs (logs take optional follow="")
- **Glance integration**: provide `glance.yml.fragment` with widget YAML using `__VARIABLE__` placeholders (substituted via envsubst); use monitor widgets for URL checking
- **Paths**: `/srv/config/<app>` (@config subvol, snapshotted) and `/srv/data/<app>` (@data subvol, no snapshots); document in PATHS.md
- **Ports**: check PORTS.md; default 8000+; apps prompt during install
- **YAML/CI**: 2-space indent; pin action versions; descriptive step names
- **Naming**: UPPER_SNAKE env vars; lowercase-dashed tags
- **Errors**: fail fast; check exit codes
- **Formatting**: ≤100 chars/line; LF endings; trim trailing whitespace

Editor rules: none (no .cursorrules or copilot-instructions.md)

