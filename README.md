# Hoth OS

A custom Almalinux-based [bootc image](https://bootc.dev) with various tools pre-installed, including:
- [Cockpit](https://cockpit-project.org/) with various plugins
- [Tailscale](https://tailscale.com/)
- [code-server](https://code-server.dev/)
- [Fish shell](https://fishshell.com/)
- [Neovim](https://neovim.io/)
- and more!

## Usage

Use Podman Quadlets to run images on your PI.

### hjust - App Management

hoth-os includes a just-based app management system accessible via the `hjust` command (available in bash/fish).

#### Available Apps

- **syncthing** - File synchronization
- **homepage** - Dashboard for all your services
- **arr-stack** - Media management (Sonarr, Radarr, Prowlarr, qBittorrent in a pod)

#### Commands

```bash
hjust <app> install      # Interactive wizard to install an app
hjust <app> uninstall    # Remove app (preserves data)
hjust <app> status       # Check app status
hjust <app> logs [follow] # View app logs
```

#### Homepage Integration

Apps can automatically add themselves to Homepage during installation. Homepage uses a config file system at `/etc/homepage/services.yaml`.

**Manual addition:**
1. Create a config file with:
   - `SERVICE_NAME` - Service name for duplicate detection
   - `YAML_CONTENT` - YAML block to append (use `__HOSTNAME__` for substitution)
2. Run: `hjust homepage add-service /path/to/config`

**Example config:**
```bash
SERVICE_NAME="My Service"
YAML_CONTENT='
- Custom Category:
    - My Service:
        icon: service.png
        href: http://__HOSTNAME__:8080
        description: My custom service
'
```

## Variants

Currently, only one variant is available:
- `hoth-os:latest` - The latest stable version of Hoth OS. Based on AlmaLinux 10 (not kitten), tested on Raspberry Pi 5.

## Links
- [AlmaLinux bootc rpi](https://github.com/AlmaLinux/bootc-images-rpi)