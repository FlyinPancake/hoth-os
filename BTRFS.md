# Btrfs Setup Guide

This guide explains how to set up btrfs subvolumes for hoth-os applications.

## Overview

hoth-os expects two directories to exist at `/srv/`:
- `/srv/config/` - Application configurations and databases (snapshotted)
- `/srv/data/` - Media files and user data (no snapshots)

Some scripts use `/var/srv/` instead of `/srv/`.
Bootc based installs symlink `/srv/` to `/var/srv/`.

These directories **must exist** before installing apps. This guide shows how to set them up as btrfs subvolumes with SSD optimizations and automated snapshots.

## Quick Setup

Use the built-in wizard to set up everything automatically:

```bash
hjust btrfs-setup
```

This will:
1. Detect available drives
2. Format the drive as btrfs (if needed)
3. Create subvolumes (@config, @data, @snapshots)
4. Optionally configure fstab and mount automatically

## Automatic Snapshots

Enable automatic snapshots of `/srv/config`:

```bash
hjust btrfs-snapshot enable    # Choose schedule (daily/hourly/weekly)
hjust btrfs-snapshot run-now   # Create snapshot immediately
hjust btrfs-snapshot status    # View timer and existing snapshots
hjust btrfs-snapshot disable   # Disable automatic snapshots
```

Snapshots are stored in `/srv/.snapshots/` and the system keeps the last 7 snapshots automatically.

## Manual Setup

If you prefer manual setup:

### 1. Create Btrfs Subvolumes

```bash
sudo mount /dev/sdX /mnt

sudo btrfs subvolume create /mnt/@config
sudo btrfs subvolume create /mnt/@data
sudo btrfs subvolume create /mnt/@snapshots

sudo umount /mnt
```

### 2. Configure Mounts

The setup script can generate a systemd mount unit for you. Alternatively, add to `/etc/fstab`:

```
UUID=your-uuid-here /var/srv/config btrfs defaults,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=@config 0 0
UUID=your-uuid-here /var/srv/data btrfs defaults,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=@data 0 0
UUID=your-uuid-here /var/srv/.snapshots btrfs defaults,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=@snapshots 0 0
```

To find your UUID:
```bash
sudo blkid /dev/sdX
```

### 3. Mount and Set Permissions

```bash
sudo mkdir -p /var/srv/{config,data,.snapshots}
sudo mount -a
sudo chown -R $(id -u):$(id -g) /var/srv/config /var/srv/data
sudo chmod 755 /var/srv/config /var/srv/data
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
hjust btrfs-snapshot status
# Note the snapshot name you want to restore

# Example services, adjust as needed
systemctl --user stop arr-stack-pod.service syncthing.service homepage.service

sudo mv /srv/config /srv/config.old

sudo btrfs subvolume snapshot /srv/.snapshots/config-TIMESTAMP /srv/config

sudo chown -R $(id -u):$(id -g) /srv/config

# Restart services
systemctl --user start arr-stack-pod.service syncthing.service homepage.service
```

## Notes

- Snapshots are read-only and kept for 7 cycles (configurable in `/usr/share/hoth-os/apps/btrfs-snapshot.sh`)
- Config snapshots protect against corruption/accidental deletion
- Data subvolume has no snapshots (large media files, not critical for backup)
- All apps expect `/srv/config` and `/srv/data` to exist before installation
- Snapshot script location: `/usr/share/hoth-os/apps/btrfs-snapshot.sh`
- Systemd units: `/usr/lib/systemd/system/btrfs-snapshot.{service,timer}`
