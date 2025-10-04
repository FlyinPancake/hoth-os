# Btrfs Setup Guide

This guide explains how to set up btrfs subvolumes for hoth-os applications.

## Overview

hoth-os expects two directories to exist at `/srv/`:
- `/srv/config/` - Application configurations and databases
- `/srv/data/` - Media files and user data

These directories **must exist** before installing apps. This guide shows how to set them up as btrfs subvolumes with SSD optimizations and automated snapshots for configs.

## Prerequisites

- External drive with btrfs filesystem
- Root/sudo access
- Drive mounted (temporarily for setup)

## Setup Steps

### 1. Create Btrfs Subvolumes

Assuming your btrfs drive is at `/dev/sdX`:

```bash
# Mount the btrfs root
sudo mount /dev/sdX /mnt

# Create subvolumes
sudo btrfs subvolume create /mnt/@config
sudo btrfs subvolume create /mnt/@data
sudo btrfs subvolume create /mnt/@snapshots

# Unmount
sudo umount /mnt
```

### 2. Configure Mounts

Add to `/etc/fstab`:

```fstab
# Btrfs config subvolume (with snapshots, SSD-optimized)
UUID=your-uuid-here  /srv/config  btrfs  subvol=@config,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2  0 0

# Btrfs data subvolume (no snapshots, SSD-optimized)
UUID=your-uuid-here  /srv/data    btrfs  subvol=@data,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2    0 0

# Snapshot storage (optional, for manual access)
UUID=your-uuid-here  /srv/.snapshots  btrfs  subvol=@snapshots,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2  0 0
```

Find your UUID:
```bash
sudo blkid /dev/sdX
```

### 3. Mount and Set Permissions

```bash
# Create mount points
sudo mkdir -p /srv/{config,data,.snapshots}

# Mount all
sudo mount -a

# Set ownership (replace 1000:1000 with your user:group)
sudo chown -R 1000:1000 /srv/config /srv/data
sudo chmod 755 /srv/config /srv/data
```

### 4. Set Up Automatic Snapshots (Optional)

Create `/usr/local/bin/snapshot-config.sh`:

```bash
#!/bin/bash
set -Eeuo pipefail

SNAPSHOT_DIR="/srv/.snapshots"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=30

# Create snapshot
sudo btrfs subvolume snapshot -r /srv/config "$SNAPSHOT_DIR/config-$TIMESTAMP"

# Clean old snapshots
find "$SNAPSHOT_DIR" -maxdepth 1 -name "config-*" -type d -mtime +$RETENTION_DAYS -exec sudo btrfs subvolume delete {} \;
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/snapshot-config.sh
```

Create systemd timer `/etc/systemd/system/snapshot-config.timer`:

```ini
[Unit]
Description=Daily snapshot of /srv/config

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Create systemd service `/etc/systemd/system/snapshot-config.service`:

```ini
[Unit]
Description=Snapshot /srv/config btrfs subvolume

[Service]
Type=oneshot
ExecStart=/usr/local/bin/snapshot-config.sh
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now snapshot-config.timer
```

## Mount Options Explained

- `noatime` - Don't update file access times (reduces writes)
- `compress=zstd:3` - Transparent compression (good balance of speed/ratio)
- `ssd` - Enable SSD-specific optimizations
- `discard=async` - Asynchronous TRIM for better performance
- `space_cache=v2` - Improved free space cache (faster mounts)

## Verification

```bash
# Check subvolumes
sudo btrfs subvolume list /srv/config

# Check mounts
mount | grep /srv

# Check snapshots (after timer runs)
sudo btrfs subvolume list /srv/.snapshots
```

## Restoring from Snapshot

To restore config from a snapshot:

```bash
# Stop all apps first
systemctl --user stop arr-stack-pod.service syncthing.service

# Move current config (backup)
sudo mv /srv/config /srv/config.old

# Restore from snapshot (replace TIMESTAMP)
sudo btrfs subvolume snapshot /srv/.snapshots/config-TIMESTAMP /srv/config

# Fix permissions
sudo chown -R $(id -u):$(id -g) /srv/config

# Start apps
systemctl --user start arr-stack-pod.service syncthing.service
```

## Notes

- Snapshots are read-only by default (use `-r` flag)
- Config snapshots protect against corruption/accidental deletion
- Data subvolume has no snapshots (large media files, not critical)
- Adjust retention policy in snapshot script as needed
- All apps expect `/srv/config` and `/srv/data` to exist before installation
