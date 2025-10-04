# Agent Guide for hoth-os
Build/lint/test:
- Build image: `just build` (alias for `podman build .`)
- Tag local image: `podman build -t local/hoth-os:dev .`
- Lint locally: `just lint` (runs `hadolint` + `actionlint`)
- CI: `lint` job (actionlint + hadolint) gates `build_bootc` and push.
- Tests: none configured; single-test not applicable yet.
Code style:
- Containerfile: group steps; prefer one `RUN` with `&&` and `set -e`.
- Packages: `dnf -y ... && dnf clean all && rm -rf /var/cache/dnf`.
- Layers: order least→most frequently changed to maximize cache.
- Shell in RUN: use `set -Eeuo pipefail`; quote variables.
- YAML: 2-space indent; pin actions by version; descriptive step names.
- justfile: kebab-case recipe names; idempotent; avoid interactive prompts.
- Naming: UPPER_SNAKE for env vars; lowercase-dashed image tags.
- Errors: fail fast; check exit codes; log commands (`set -x` for debug).
- Formatting: lines ≤100 chars; trim trailing whitespace; use LF endings.
Editor/automation:
- Cursor/Copilot rules: none found; nothing to include.
