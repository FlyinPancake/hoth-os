#!/bin/bash
set -Eeuo pipefail

SNAPSHOT_DIR="/srv/.snapshots"
CONFIG_DIR="/srv/config"
MAX_SNAPSHOTS=7

if [ ! -d "$CONFIG_DIR" ]; then
    echo "Error: $CONFIG_DIR does not exist"
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
