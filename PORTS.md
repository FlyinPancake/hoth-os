# Port Allocations

| Port | Service | State | Notes |
|------|---------|-------|-------|
| 9090 | Cockpit | Enabled by default | System management web UI |
| 8384 | Syncthing | User-installed | Web UI for file sync |
| 22000 | Syncthing | User-installed | TCP/UDP data transfer |
| 21027 | Syncthing | User-installed | UDP discovery |
| 8090 | Homepage | User-installed | Dashboard (configurable during install) |

## Reserved Ports
- 9090: Cockpit (always enabled)

## Notes
- User-installed apps can have their ports customized during the `hjust <app> install` wizard
- Cockpit port cannot be changed as it's a system service
- Homepage defaults to 8090 but prompts during installation
