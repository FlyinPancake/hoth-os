# Hoth OS

An opinionated, easy-to-use, terminal-first OS for self-hosting on Raspberry Pi.

Hoth OS is Almalinux-based [bootc image](https://bootc.dev) with various tools pre-installed, including:
- [Cockpit](https://cockpit-project.org/) with various plugins
- [Tailscale](https://tailscale.com/)
- [code-server](https://code-server.dev/)
- [Fish shell](https://fishshell.com/)
- [Neovim](https://neovim.io/)
- and more!

It relies heavily on [Podman](https://podman.io/) and Quadlets (podman systemd integration) for app management, with a simple just-based CLI for installing and managing apps.

### hjust - OS Management

hoth-os includes a just-based OS management system accessible via the `hjust` command (available in bash/fish).

#### Initial Setup

If you have an external drive, set it up with Btrfs and create the necessary subvolumes:

```bash
hjust btrfs-setup           # Interactive wizard for drive setup
hjust btrfs-snapshot enable # Enable automatic config snapshots
```

See [BTRFS.md](BTRFS.md) for details.

#### Available Apps

- **syncthing** - File synchronization
- **homepage** - Dashboard for all your services
- **arr-stack** - Media management (Sonarr, Radarr, Prowlarr, qBittorrent in a pod)

#### Commands

```bash
# App management
hjust <app> install      # Interactive wizard to install an app
hjust <app> uninstall    # Remove app (preserves data)
hjust <app> status       # Check app status
hjust <app> logs [follow] # View app logs

# System management
hjust btrfs-setup        # Set up btrfs storage
hjust btrfs-snapshot     # Manage automatic snapshots
hjust starship           # Enable/disable Starship prompt
hjust update             # Update system
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

## Roadmap

- [ ] Recommended tech stack for access --
  This would include a guide for setting up Tailscale and some kind of basic open-to-internet access (e.g. Pangolin or Tailscale Funnel).
- [ ] More apps (e.g., Nextcloud, Home Assistant) -- If you have suggestions, please open an issue!
- [ ] x86_64 support --
  This project started with me wanting a ready to run, image-based OS for my Raspberry Pi 5. I may add x86_64 support in the future if there's enough interest.
- [ ] Better ASCII art for the terminal login screen :)
- [ ] More setup options (e.g., automated TLS with Let's Encrypt, domain setup) --
  I'm not really sure how to approach this yet, but it's on my mind.
- [ ] Integration with some local OIDC provider (e.g., PocketID or Authentik) for single sign-on across services. -- 
  This is a bit tricky, since some of the services that I want to be first-class citizens don't really support OIDC well (e.g., qBittorrent). But it's something I want to explore.

## Inspiration

### umbrelOS
- [GitHub Repository](https://github.com/getumbrel/umbrel)
- [Website](https://umbrel.com/)

umbrelOS is a popular OS for running Bitcoin and Lightning nodes, along with other self-hosted apps. Hoth OS draws inspiration from its user-friendly approach to app management and system configuration.
The main difference is that Hoth OS is terminal-first (more so terminal only) and has no aims for cryptocurrency integration.

### universal-blue (mostly ucore)
- [GitHub Organization](https://github.com/ublue-os)
- [Website](https://universal-blue.org/)

I have a running ucore install on my server and I love it to bits. It's a great example of a minimal, container-focused OS that prioritizes user control and simplicity.
I also run Bazzite on my desktop, which is another great project from the ublue umbrella.
In particular, Bazzite (and Bluefin or Aurora) have a ton of setup scripts for various apps that I have drawn inspiration from for Hoth OS.

And finally, Justfiles rule. :)

### Omarchy
- [GitHub Repository](https://github.com/basecamp/omarchy)
- [Website](https://omarchy.org/)

The basic principles of this project can be derived from the former two projects, but the thing that set my mind on this path was using Omarchy.
I have some experience with people who would not touch a window manager with a ten-foot pole, but they were thinking about it because Omarchy made it so easy.
I wanted to apply that same well-thought-out simplicity to a terminal-first OS for self-hosting.
Let's see how it goes!

## Upstream
- [AlmaLinux bootc rpi](https://github.com/AlmaLinux/bootc-images-rpi)