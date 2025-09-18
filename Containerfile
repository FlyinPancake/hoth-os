FROM quay.io/almalinuxorg/almalinux-bootc-rpi:10

# Make update dnf cache
RUN dnf install -y dnf-plugins-core && dnf config-manager --set-enabled crb && dnf install -y epel-release

# Install packages
RUN dnf install -y vim fish

# Install tailscale
RUN <<EORUN
dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora//tailscale.repo
dnf install -y tailscale
systemctl enable tailscaled
EORUN

# Clean up dnf cache to reduce image size
RUN dnf clean all