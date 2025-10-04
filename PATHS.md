# Default Paths

This document lists all default paths used by hoth-os applications and system components.

## System Paths

| Path | Purpose | Notes |
|------|---------|-------|
| `/usr/share/hoth-os/` | System files | Read-only installation directory |
| `/usr/share/hoth-os/apps/` | App definitions | Each app in its own subdirectory |
| `/usr/share/hoth-os/quadlets/` | Systemd quadlet templates | Copied to user config on install |
| `$HOME/.config/containers/systemd/` | Active quadlet files | User-specific systemd container configs |

## Btrfs Structure

The default configuration uses btrfs subvolumes on external storage mounted at `/srv/`:

| Path | Type | Purpose | Snapshots |
|------|------|---------|-----------|
| `/srv/config/` | Btrfs subvolume (@config) | Application configs & databases | Enabled |
| `/srv/data/` | Btrfs subvolume (@data) | Media files & user data | Disabled |
| `/srv/.snapshots/` | Directory | Snapshot storage for @config | N/A |

### Mount Options (SSD-optimized)
- `noatime` - Don't update access times
- `compress=zstd:3` - Transparent compression
- `ssd` - SSD-specific optimizations
- `discard=async` - Async TRIM support
- `space_cache=v2` - Improved free space cache

See [BTRFS.md](BTRFS.md) for setup instructions.

## Application Data Paths

### Syncthing
| Path | Purpose | Subvolume |
|------|---------|-----------|
| `/srv/config/syncthing/` | Syncthing configuration | @config |
| `/srv/data/syncthing/` | Synchronized files | @data |

### Arr Stack
| Path | Purpose | Subvolume |
|------|---------|-----------|
| `/srv/config/sonarr/` | Sonarr config and database | @config |
| `/srv/config/radarr/` | Radarr config and database | @config |
| `/srv/config/prowlarr/` | Prowlarr config and database | @config |
| `/srv/config/qbittorrent/` | qBittorrent config | @config |
| `/srv/data/downloads/` | Download directory (shared) | @data |
| `/srv/data/tv/` | TV series library | @data |
| `/srv/data/movies/` | Movie library | @data |

### Homepage
| Path | Purpose |
|------|---------|
| `/etc/homepage/` | Configuration directory |
| `/etc/homepage/services.yaml` | Service definitions |
| `/etc/homepage/bookmarks.yaml` | Bookmark definitions |
| `/etc/homepage/widgets.yaml` | Widget definitions |
| `/etc/homepage/settings.yaml` | General settings |
| `/etc/homepage/docker.yaml` | Docker integration config |

## App Configuration Templates

| Path | Purpose |
|------|---------|
| `/usr/share/hoth-os/apps/<app>/justfile` | App installer recipes |
| `/usr/share/hoth-os/apps/<app>/homepage_config.sh` | Homepage integration template |
| `/usr/share/hoth-os/apps/<app>/config/` | Default config files (optional) |

## Notes

- `/srv/config/` and `/srv/data/` directories are created during app installation
- Quadlet files are copied from `/usr/share/hoth-os/quadlets/` to `$HOME/.config/containers/systemd/` on install
- Homepage configs use `__VARIABLE__` placeholders that are substituted during configuration
- Data paths are bind-mounted into containers via quadlet definitions
- Btrfs subvolumes should be created before installing apps (see BTRFS.md)
