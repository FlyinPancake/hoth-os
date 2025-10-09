# Port Allocations

| Port | Service | State | Notes |
|------|---------|-------|-------|
| 9090 | Cockpit | Enabled by default | System management web UI |
| 8384 | Syncthing | User-installed | Web UI for file sync |
| 22000 | Syncthing | User-installed | TCP/UDP data transfer |
| 21027 | Syncthing | User-installed | UDP discovery |
| 8090 | Glance | User-installed | Dashboard (configurable during install) |
| 8989 | Sonarr | User-installed | TV series manager (configurable during install) |
| 7878 | Radarr | User-installed | Movie manager (configurable during install) |
| 9696 | Prowlarr | User-installed | Indexer manager (configurable during install) |
| 8080 | qBittorrent | User-installed | Torrent client web UI (configurable during install) |
| 6881 | qBittorrent | User-installed | TCP/UDP torrent traffic (configurable during install) |

## Reserved Ports
- 9090: Cockpit (always enabled)

## Notes
- User-installed apps can have their ports customized during the `hjust <app> install` wizard
- Cockpit port cannot be changed as it's a system service
- Glance defaults to 8090 but prompts during installation
