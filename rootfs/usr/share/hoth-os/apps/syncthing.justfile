set shell := ["bash", "-Eeuo", "pipefail", "-c"]

install:
    #!/usr/bin/env bash
    set -Eeuo pipefail
    
    gum style --border rounded --padding "1 2" --border-foreground 212 "Syncthing Setup Wizard"
    
    DATA_PATH=$(gum input --placeholder "/var/syncthing" --prompt "Data path: " --value "/var/syncthing")
    WEB_PORT=$(gum input --placeholder "8384" --prompt "Web UI port: " --value "8384")
    DEVICE_NAME=$(gum input --placeholder "hoth-pi" --prompt "Device name: " --value "hoth-pi")
    
    gum confirm "Install Syncthing with these settings?" || exit 0
    
    gum spin --spinner dot --title "Creating directories..." -- mkdir -p "$DATA_PATH"
    
    mkdir -p "$HOME/.config/containers/systemd"
    
    gum spin --spinner dot --title "Installing quadlet..." -- sed \
        -e "s|PublishPort=8384:8384|PublishPort=$WEB_PORT:8384|" \
        -e "s|Volume=/var/syncthing:/var/syncthing:Z|Volume=$DATA_PATH:/var/syncthing:Z|" \
        /usr/share/hoth-os/quadlets/syncthing.container \
        > "$HOME/.config/containers/systemd/syncthing.container"
    
    gum spin --spinner dot --title "Starting service..." -- bash -c "systemctl --user daemon-reload && systemctl --user enable --now syncthing.service"
    
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
