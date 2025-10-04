SERVICE_NAME="Syncthing"
YAML_CONTENT='
    - Syncthing:
        icon: syncthing.png
        href: http://__HOSTNAME__:__PORT__
        description: File synchronization
        widget:
          type: strelaysrv
          url: http://__HOSTNAME__:__PORT__
'
