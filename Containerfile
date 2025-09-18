FROM quay.io/almalinuxorg/almalinux-bootc-rpi:10

# Make update dnf cache
RUN dnf install -y dnf-plugins-core && dnf config-manager --set-enabled crb && dnf install -y epel-release

# Install packages
RUN dnf install -y vim fish

# Install tailscale
RUN dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora//tailscale.repo && \
    dnf install -y tailscale && \
    systemctl enable tailscaled

# Clean up dnf cache to reduce image size
RUN dnf clean all


LABEL org.opencontainers.image.source="https://github.com/flyinpancake/hoth-os"
LABEL org.opencontainers.image.description="A minimal OS for Raspberry Pi based on AlmaLinux"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="hoth-os"
