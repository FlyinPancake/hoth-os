#!/bin/bash
set -Eeuo pipefail

gum style --border rounded --padding "1 2" --border-foreground 212 "Btrfs Setup for hoth-os"
echo

gum style --faint "This script will help you set up btrfs subvolumes for hoth-os."
gum style --faint "Prerequisites:"
gum style --faint "  - External drive with btrfs filesystem"
gum style --faint "  - Drive temporarily mounted (e.g., at /mnt)"
gum style --faint "  - Root/sudo access"
echo

gum confirm "Continue with btrfs setup?" || exit 0
echo

MOUNT_POINT=$(gum input --placeholder "/mnt" --prompt "Temporary mount point of btrfs drive: " --value "/mnt")
echo "Mount point: $MOUNT_POINT"
echo

if ! mountpoint -q "$MOUNT_POINT"; then
    gum style --foreground 196 "Error: $MOUNT_POINT is not a mount point"
    exit 1
fi

if ! sudo btrfs filesystem show "$MOUNT_POINT" &>/dev/null; then
    gum style --foreground 196 "Error: $MOUNT_POINT is not a btrfs filesystem"
    exit 1
fi

gum style --foreground 212 "Creating btrfs subvolumes..."

if sudo btrfs subvolume show "$MOUNT_POINT/@config" &>/dev/null; then
    gum style --foreground 220 "  @config already exists, skipping"
else
    sudo btrfs subvolume create "$MOUNT_POINT/@config"
    gum style --foreground 212 "  ✓ Created @config"
fi

if sudo btrfs subvolume show "$MOUNT_POINT/@data" &>/dev/null; then
    gum style --foreground 220 "  @data already exists, skipping"
else
    sudo btrfs subvolume create "$MOUNT_POINT/@data"
    gum style --foreground 212 "  ✓ Created @data"
fi

if sudo btrfs subvolume show "$MOUNT_POINT/@snapshots" &>/dev/null; then
    gum style --foreground 220 "  @snapshots already exists, skipping"
else
    sudo btrfs subvolume create "$MOUNT_POINT/@snapshots"
    gum style --foreground 212 "  ✓ Created @snapshots"
fi

echo

DEVICE=$(findmnt -n -o SOURCE "$MOUNT_POINT")
UUID=$(sudo blkid -s UUID -o value "$DEVICE")

gum style --foreground 212 "Btrfs subvolumes created successfully!"
echo
gum style --faint "Device: $DEVICE"
gum style --faint "UUID: $UUID"
echo

gum style --border rounded --padding "1 2" --border-foreground 212 "Next Steps"
echo
gum style "1. Add to /etc/fstab:"
echo
cat << EOF
UUID=$UUID  /srv/config      btrfs  subvol=@config,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2  0 0
UUID=$UUID  /srv/data        btrfs  subvol=@data,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2    0 0
UUID=$UUID  /srv/.snapshots  btrfs  subvol=@snapshots,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2  0 0
EOF
echo
gum style "2. Create mount points and mount:"
echo
cat << EOF
sudo mkdir -p /srv/{config,data,.snapshots}
sudo mount -a
sudo chown -R \$(id -u):\$(id -g) /srv/config /srv/data
sudo chmod 755 /srv/config /srv/data
EOF
echo
gum style "3. Set up automatic snapshots (optional):"
gum style --faint "   See BTRFS.md for snapshot configuration"
echo
