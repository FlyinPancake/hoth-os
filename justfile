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

# Copy a file from rootfs/<path> to <path> on a remote system via SSH

# Usage: just copy-to-remote <ssh-address> <rootfs-path>
copy-to-remote ssh_address rootfs_path:
    #!/bin/bash
    set -Eeuo pipefail

    # Check if source file exists
    if [ ! -f "{{ rootfs_path }}" ]; then
        echo "Error: Source file '{{ rootfs_path }}' does not exist"
        exit 1
    fi

    # Extract the path without rootfs/ prefix for remote destination
    remote_path=$(echo "{{ rootfs_path }}" | sed 's|^rootfs/||')
    file_name=$(basename "$remote_path")

    # Create remote directory if needed and copy file
    echo "Copying '{{ rootfs_path }}' to '{{ ssh_address }}:$remote_path'..."
    scp "{{ rootfs_path }}" "{{ ssh_address }}:$file_name"
    ssh "{{ ssh_address }}" "sudo mv $file_name /$remote_path"

    echo "File copied successfully"
