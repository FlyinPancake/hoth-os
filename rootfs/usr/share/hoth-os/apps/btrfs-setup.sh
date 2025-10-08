#!/bin/bash
set -Eeuo pipefail

gum style --border rounded --padding "1 2" --border-foreground 212 "Btrfs Setup for hoth-os"
echo

gum style --faint "This script will help you set up btrfs subvolumes for hoth-os."
echo

gum confirm "Continue with btrfs setup?" || exit 0
echo

gum style --foreground 212 "Detecting available block devices..."
echo

DEVICES=$(lsblk -ndo NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT | grep "disk" | awk '{print $1 " (" $2 ")"}')

if [ -z "$DEVICES" ]; then
    gum style --foreground 196 "Error: No block devices found"
    exit 1
fi

DEVICE_NAME=$(echo "$DEVICES" | gum choose --header "Select drive to use:")
DEVICE="/dev/$(echo "$DEVICE_NAME" | awk '{print $1}')"
echo "Selected device: $DEVICE"
echo

CURRENT_FSTYPE=$(lsblk -ndo FSTYPE "$DEVICE" || echo "")
CURRENT_MOUNT=$(lsblk -ndo MOUNTPOINT "$DEVICE" || echo "")

if [ -n "$CURRENT_MOUNT" ]; then
    gum style --foreground 220 "Warning: Device is currently mounted at $CURRENT_MOUNT"
    if gum confirm "Unmount $DEVICE before continuing?"; then
        sudo umount "$DEVICE" || true
    else
        gum style --foreground 196 "Cannot proceed with mounted device"
        exit 1
    fi
fi

if [ "$CURRENT_FSTYPE" != "btrfs" ]; then
    gum style --foreground 220 "Warning: Device is not formatted as btrfs (current: ${CURRENT_FSTYPE:-none})"
    gum style --foreground 196 "THIS WILL ERASE ALL DATA ON $DEVICE"
    echo
    if gum confirm --default=false "Format $DEVICE as btrfs?"; then
        gum style --foreground 212 "Formatting $DEVICE as btrfs..."
        sudo mkfs.btrfs -f "$DEVICE"
        gum style --foreground 212 "✓ Formatted successfully"
        echo
    else
        gum style --foreground 196 "Cannot proceed without btrfs filesystem"
        exit 1
    fi
fi

MOUNT_POINT="/mnt/btrfs-setup-$(date +%s)"
gum style --foreground 212 "Mounting $DEVICE at $MOUNT_POINT..."
sudo mkdir -p "$MOUNT_POINT"
sudo mount "$DEVICE" "$MOUNT_POINT"
echo "Mounted at: $MOUNT_POINT"
echo

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

UUID=$(sudo blkid -s UUID -o value "$DEVICE")

gum style --foreground 212 "Unmounting temporary mount point..."
sudo umount "$MOUNT_POINT"
sudo rmdir "$MOUNT_POINT"

gum style --foreground 212 "Btrfs subvolumes created successfully!"
echo
gum style --faint "Device: $DEVICE"
gum style --faint "UUID: $UUID"
echo

if gum confirm "Apply configuration now (add systemd mount units and mount)?"; then
    echo
    gum style --foreground 212 "Creating systemd mount units..."
    for SUBVOL in config data .snapshots; do
        MOUNT_PATH="/var/srv/$SUBVOL"
        UNIT_PATH="/etc/systemd/system/srv-$SUBVOL.mount"
        OPTIONS="subvol=@$SUBVOL,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2"
        
        if [ -f "$UNIT_PATH" ]; then
            gum style --foreground 220 "  $UNIT_PATH already exists, skipping"
        else
            sudo sed -e "s|__UUID__|$UUID|g" \
                     -e "s|__MOUNT_POINT__|$MOUNT_PATH|g" \
                     -e "s|__FS_TYPE__|btrfs|g" \
                     -e "s|__OPTIONS__|$OPTIONS|g" \
                     /usr/share/hoth-os/disks/mount_template.mount | sudo tee "$UNIT_PATH" > /dev/null
            sudo systemctl enable "srv-$SUBVOL.mount"
            gum style --foreground 212 "  ✓ Created and enabled $UNIT_PATH"
        fi

    gum style --foreground 212 "Setting permissions..."
    sudo chown -R "$(id -u):$(id -g)" /var/srv/config /var/srv/data
    sudo chmod 755 /var/srv/config /var/srv/data
    gum style --foreground 212 "✓ Permissions set"
    echo
    
    gum style --foreground 212 "✓ Setup complete!"
    echo
    gum style --faint "Mounted at:"
    gum style --faint "  /var/srv/config (config & databases, with snapshots)"
    gum style --faint "  /var/srv/data (media & downloads, no snapshots)"
    gum style --faint "  /var/srv/.snapshots (snapshot storage)"
    echo
    gum style --faint "For automatic snapshots, see BTRFS.md"
else
    echo
    gum style --border rounded --padding "1 2" --border-foreground 212 "Manual Setup Instructions"
    echo
    gum style --faint "To complete the setup, create the following mount units and mount them:"
    echo
    for SUBVOL in config data .snapshots; do
        MOUNT_PATH="/var/srv/$SUBVOL"
        gum style --faint "  $MOUNT_PATH"
    done
    echo
    gum style --faint "Then set permissions:"
    gum style --faint "  sudo chown -R \$(id -u):\$(id -g) /var/srv/config /var/srv/data"
    gum style --faint "  sudo chmod 755 /var/srv/config /var/srv/data"
    echo
    gum style --faint "For automatic snapshots, see BTRFS.md in the hoth-os repository."
fi
