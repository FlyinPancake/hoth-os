default:
    just --choose

build:
    podman build .

lint-containerfile:
    #!/bin/bash
    if command -v hadolint >/dev/null 2>&1; then \
        hadolint Containerfile; \
    else \
        podman run --rm -v "$PWD:/work:ro,Z" -w /work docker.io/hadolint/hadolint hadolint Containerfile; \
    fi

lint-actions:
    #!/bin/bash
    if command -v actionlint >/dev/null 2>&1; then \
        actionlint; \
    else \
        podman run --rm -v "$PWD:/repo:ro,Z" -w /repo docker.io/rhysd/actionlint:latest; \
    fi

lint:
    just lint-containerfile
    just lint-actions
