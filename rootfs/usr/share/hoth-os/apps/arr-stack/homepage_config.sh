SERVICE_NAME="Media Management"
YAML_CONTENT='
- Media Management:
    - Sonarr:
        icon: sonarr.png
        href: http://__HOSTNAME__:__SONARR_PORT__
        description: TV series manager
        widget:
          type: sonarr
          url: http://__HOSTNAME__:__SONARR_PORT__
          key: __SONARR_API__
    - Radarr:
        icon: radarr.png
        href: http://__HOSTNAME__:__RADARR_PORT__
        description: Movie manager
        widget:
          type: radarr
          url: http://__HOSTNAME__:__RADARR_PORT__
          key: __RADARR_API__
    - Prowlarr:
        icon: prowlarr.png
        href: http://__HOSTNAME__:__PROWLARR_PORT__
        description: Indexer manager
        widget:
          type: prowlarr
          url: http://__HOSTNAME__:__PROWLARR_PORT__
          key: __PROWLARR_API__
    - qBittorrent:
        icon: qbittorrent.png
        href: http://__HOSTNAME__:__QBIT_PORT__
        description: Torrent client
        widget:
          type: qbittorrent
          url: http://__HOSTNAME__:__QBIT_PORT__
          username: __QBIT_USER__
          password: __QBIT_PASS__
'
