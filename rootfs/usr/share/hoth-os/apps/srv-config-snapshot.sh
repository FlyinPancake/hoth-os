#!/bin/bash
set -Eeuo pipefail

SNAPSHOT_DIR="/var/srv/.snapshots"
SRV_CONFIG_DIR="/var/srv/config"

SNAPSHOT_CONFIG_FILE="/etc/hoth-os/btrfs-snapshot.conf"

DEFAULT_MAX_SNAPSHOTS=7

if [ ! -f "$SNAPSHOT_CONFIG_FILE" ]; then
    echo "Creating default config at $SNAPSHOT_CONFIG_FILE"
    sudo mkdir -p "$(dirname "$SNAPSHOT_CONFIG_FILE")"
    sudo chown "$(id -u):$(id -g)" "$(dirname "$SNAPSHOT_CONFIG_FILE")"
    touch "$SNAPSHOT_CONFIG_FILE"
fi

MAX_SNAPSHOTS=$(yq e '.max_snapshots' -p ini -o ini "$SNAPSHOT_CONFIG_FILE")

if ! [[ "$MAX_SNAPSHOTS" =~ ^[0-9]+$ ]]; then
    echo "Invalid max_snapshots in config, using default ($DEFAULT_MAX_SNAPSHOTS)"
    MAX_SNAPSHOTS=$DEFAULT_MAX_SNAPSHOTS
    yq e -i ".max_snapshots = $DEFAULT_MAX_SNAPSHOTS" -p ini -o ini "$SNAPSHOT_CONFIG_FILE"
fi


if [ ! -d "$SRV_CONFIG_DIR" ]; then
    echo "Error: $SRV_CONFIG_DIR does not exist"
    exit 1
fi

if [ ! -d "$SNAPSHOT_DIR" ]; then
    echo "Error: $SNAPSHOT_DIR does not exist"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SNAPSHOT_NAME="config-$TIMESTAMP"

echo "Creating snapshot: $SNAPSHOT_NAME"
btrfs subvolume snapshot -r "$CONFIG_DIR" "$SNAPSHOT_DIR/$SNAPSHOT_NAME"

echo "Cleaning up old snapshots (keeping last $MAX_SNAPSHOTS)..."
SNAPSHOTS=$(ls -1 "$SNAPSHOT_DIR" | grep "^config-" | sort -r)
SNAPSHOT_COUNT=$(echo "$SNAPSHOTS" | wc -l)

if [ "$SNAPSHOT_COUNT" -gt "$MAX_SNAPSHOTS" ]; then
    echo "$SNAPSHOTS" | tail -n +$((MAX_SNAPSHOTS + 1)) | while read -r old_snapshot; do
        echo "Deleting old snapshot: $old_snapshot"
        btrfs subvolume delete "$SNAPSHOT_DIR/$old_snapshot"
    done
fi

echo "Snapshot created successfully: $SNAPSHOT_NAME"
