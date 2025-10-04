FROM quay.io/almalinuxorg/almalinux-bootc-rpi:10

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install and configure repositories, packages, then clean up in one layer
# hadolint ignore=DL3041
RUN dnf -y install dnf-plugins-core && \
    dnf config-manager --set-enabled crb && \
    dnf -y install epel-release && \
    dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo && \
    dnf -y copr enable tkbcopr/fd && \
    dnf -y install \
    vim fish cockpit cockpit-ostree cockpit-files cockpit-podman neovim tailscale ripgrep fd btop just gum yq fzf \
    https://github.com/45Drives/cockpit-file-sharing/releases/download/v4.3.1-2/cockpit-file-sharing-4.3.1-2.el9.noarch.rpm \
    https://github.com/45Drives/cockpit-identities/releases/download/v0.1.12/cockpit-identities-0.1.12-1.el8.noarch.rpm \
    https://github.com/coder/code-server/releases/download/v4.104.2/code-server-4.104.2-arm64.rpm && \
    dnf -y update && \
    dnf clean all && rm -rf /var/cache/dnf && \
    systemctl enable tailscaled && \
    curl -sS https://starship.rs/install.sh | sh -s -- -y

COPY rootfs/ /

LABEL org.opencontainers.image.source="https://github.com/flyinpancake/hoth-os"
LABEL org.opencontainers.image.description="A minimal OS for Raspberry Pi based on AlmaLinux"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="hoth-os"
