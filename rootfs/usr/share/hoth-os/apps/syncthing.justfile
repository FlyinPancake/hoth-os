set shell := ["bash", "-Eeuo", "pipefail", "-c"]

install:
    #!/usr/bin/env bash
    set -Eeuo pipefail
    
    gum style --border rounded --padding "1 2" --border-foreground 212 "Syncthing Setup Wizard"
    echo
    
    DATA_PATH=$(gum input --placeholder "/var/syncthing" --prompt "Data path: " --value "/var/syncthing")
    echo "Data path: $DATA_PATH"
    
    WEB_PORT=$(gum input --placeholder "8384" --prompt "Web UI port: " --value "8384")
    echo "Web UI port: $WEB_PORT"
    
    DEVICE_NAME=$(gum input --placeholder "hoth-pi" --prompt "Device name: " --value "hoth-pi")
    echo "Device name: $DEVICE_NAME"
    echo
    
    gum confirm "Install Syncthing with these settings?" || exit 0
    echo
    
    echo "Creating directories..."
    sudo mkdir -p "$DATA_PATH"
    sudo chown $(id -u):$(id -g) "$DATA_PATH"
    
    QUADLET_DIR="$HOME/.config/containers/systemd"
    mkdir -p "$QUADLET_DIR"
    
    echo "Installing quadlet..."
    sed \
        -e "s|PublishPort=8384:8384|PublishPort=$WEB_PORT:8384|" \
        -e "s|Volume=/var/syncthing:/var/syncthing:Z|Volume=$DATA_PATH:/var/syncthing:Z|" \
        -e "s|PUID=1000|PUID=$(id -u)|" \
        -e "s|PGID=1000|PGID=$(id -g)|" \
        /usr/share/hoth-os/quadlets/syncthing.container \
        > "$QUADLET_DIR/syncthing.container"
    
    loginctl enable-linger $(whoami)
    
    echo "Starting service..."
    systemctl --user daemon-reload
    systemctl --user start syncthing.service
    echo
    
    gum style --foreground 212 "✓ Syncthing installed successfully!"
    gum style --faint "Web UI: http://localhost:$WEB_PORT | Data: $DATA_PATH"
    gum style --faint "Device name: $DEVICE_NAME (configure in web UI)"

uninstall:
    #!/usr/bin/env bash
    set -Eeuo pipefail
    
    gum confirm --default=false "Uninstall Syncthing? (data will be preserved)" || exit 0
    
    gum spin --spinner dot --title "Stopping service..." -- systemctl --user disable --now syncthing.service 2>/dev/null || true
    rm -f "$HOME/.config/containers/systemd/syncthing.container"
    systemctl --user daemon-reload
    
    gum style --foreground 212 "✓ Syncthing uninstalled"

status:
    @systemctl --user status syncthing.service

logs follow="":
    #!/usr/bin/env bash
    if [[ "{{follow}}" == "follow" || "{{follow}}" == "f" ]]; then
        journalctl --user -u syncthing.service -f
    else
        journalctl --user -u syncthing.service -n 50
    fi
