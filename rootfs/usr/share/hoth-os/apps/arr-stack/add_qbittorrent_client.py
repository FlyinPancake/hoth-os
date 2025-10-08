#!/usr/bin/env python3
"""
Add qBittorrent as a download client to Sonarr and Radarr via their APIs.

Requirements:
- Python 3.8+
- requests (pip install requests)

Usage examples:
  # Add qBittorrent to both Sonarr and Radarr
  python add_qbittorrent_client.py \
    --sonarr-url http://localhost:8989 \
    --sonarr-apikey <SONARR_API_KEY> \
    --radarr-url http://localhost:7878 \
    --radarr-apikey <RADARR_API_KEY> \
    --qbittorrent-url http://localhost:8080 \
    --qbittorrent-username <USERNAME> \
    --qbittorrent-password <PASSWORD>

  # Add qBittorrent to only Sonarr
  python add_qbittorrent_client.py \
    --sonarr-url http://localhost:8989 \
    --sonarr-apikey <SONARR_API_KEY> \
    --qbittorrent-url http://localhost:8080 \
    --qbittorrent-username <USERNAME> \
    --qbittorrent-password <PASSWORD>
"""

import argparse
import sys
import requests
from urllib.parse import urljoin


def _headers(api_key: str) -> dict:
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _get_json(url: str, headers: dict, verify: bool) -> list | dict:
    r = requests.get(url, headers=headers, timeout=15, verify=verify)
    if r.status_code >= 400:
        raise RuntimeError(f"GET {url} failed: {r.status_code} {r.text}")
    return r.json()


def _post_json(url: str, headers: dict, payload: dict, verify: bool) -> dict:
    r = requests.post(url, headers=headers, json=payload, timeout=30, verify=verify)
    if r.status_code >= 400:
        raise RuntimeError(f"POST {url} failed: {r.status_code} {r.text}")
    return r.json()


def _normalize_base_url(u: str) -> str:
    # Ensure no trailing slash for baseUrl fields
    return u.rstrip("/")


def add_qbittorrent_to_sonarr(
    sonarr_url: str,
    sonarr_api_key: str,
    qbittorrent_url: str,
    qbittorrent_username: str,
    qbittorrent_password: str,
    qbittorrent_port: int,
    *,
    verify_tls: bool = True,
) -> dict:
    """Add qBittorrent as a download client to Sonarr."""
    sonarr_url = _normalize_base_url(sonarr_url)
    qbittorrent_url = _normalize_base_url(qbittorrent_url)
    headers = _headers(sonarr_api_key)

    # Get download client schemas to find qBittorrent
    schema_url = urljoin(sonarr_url + "/", "api/v3/downloadclient/schema")
    schemas = _get_json(schema_url, headers, verify_tls)

    if not isinstance(schemas, list) or not schemas:
        raise RuntimeError("No download client schemas returned by Sonarr.")

    # Find qBittorrent schema
    qbittorrent_schema = None
    for schema in schemas:
        if schema.get("implementation") == "QBittorrent":
            qbittorrent_schema = schema
            break

    if not qbittorrent_schema:
        raise RuntimeError("qBittorrent schema not found in Sonarr.")

    # Prepare fields from schema
    fields = qbittorrent_schema.get("fields", []) or []

    # Set required fields
    field_map = {
        "host": "localhost",
        "port": qbittorrent_port,
        "urlBase": "",
        "username": qbittorrent_username,
        "password": qbittorrent_password,
        "category": "sonarr",
        "recentTvPriority": 0,  # Normal
        "olderTvPriority": 0,  # Normal
        "initialPriority": 0,  # Normal
        "useSsl": False,
        "addPaused": False,
    }

    for field in fields:
        field_name = field.get("name")
        if field_name in field_map:
            field["value"] = field_map[field_name]

    # Build payload
    payload = {
        "enable": True,
        "protocol": "torrent",
        "priority": 1,
        "name": "qBittorrent",
        "implementation": "qBittorrent",
        "implementationName": "qBittorrent",
        "configContract": "qBittorrentSettings",
        "tags": [],
        "fields": fields,
    }

    # Create the download client
    create_url = urljoin(sonarr_url + "/", "api/v3/downloadclient")
    created = _post_json(create_url, headers, payload, verify_tls)
    return created


def add_qbittorrent_to_radarr(
    radarr_url: str,
    radarr_api_key: str,
    qbittorrent_url: str,
    qbittorrent_username: str,
    qbittorrent_password: str,
    qbittorrent_port: int,
    *,
    verify_tls: bool = True,
) -> dict:
    """Add qBittorrent as a download client to Radarr."""
    radarr_url = _normalize_base_url(radarr_url)
    qbittorrent_url = _normalize_base_url(qbittorrent_url)
    headers = _headers(radarr_api_key)

    # Get download client schemas to find qBittorrent
    schema_url = urljoin(radarr_url + "/", "api/v3/downloadclient/schema")
    schemas = _get_json(schema_url, headers, verify_tls)

    if not isinstance(schemas, list) or not schemas:
        raise RuntimeError("No download client schemas returned by Radarr.")

    # Find qBittorrent schema
    qbittorrent_schema = None
    for schema in schemas:
        if schema.get("implementation") == "QBittorrent":
            qbittorrent_schema = schema
            break

    if not qbittorrent_schema:
        raise RuntimeError("qBittorrent schema not found in Radarr.")

    # Prepare fields from schema
    fields = qbittorrent_schema.get("fields", []) or []

    # Set required fields
    field_map = {
        "host": "localhost",
        "port": qbittorrent_port,
        "urlBase": "",
        "username": qbittorrent_username,
        "password": qbittorrent_password,
        "category": "radarr",
        "recentMoviePriority": 0,  # Normal
        "olderMoviePriority": 0,  # Normal
        "initialPriority": 0,  # Normal
        "useSsl": False,
        "addPaused": False,
    }

    for field in fields:
        field_name = field.get("name")
        if field_name in field_map:
            field["value"] = field_map[field_name]

    # Build payload
    payload = {
        "enable": True,
        "protocol": "torrent",
        "priority": 1,
        "name": "qBittorrent",
        "implementation": "qBittorrent",
        "implementationName": "qBittorrent",
        "configContract": "qBittorrentSettings",
        "tags": [],
        "fields": fields,
    }

    # Create the download client
    create_url = urljoin(radarr_url + "/", "api/v3/downloadclient")
    created = _post_json(create_url, headers, payload, verify_tls)
    return created


def main():
    parser = argparse.ArgumentParser(
        description="Add qBittorrent as a download client to Sonarr and Radarr."
    )
    parser.add_argument(
        "--sonarr-url",
        help="Sonarr base URL (e.g., http://localhost:8989)",
    )
    parser.add_argument("--sonarr-apikey", help="Sonarr API key")
    parser.add_argument(
        "--radarr-url",
        help="Radarr base URL (e.g., http://localhost:7878)",
    )
    parser.add_argument("--radarr-apikey", help="Radarr API key")
    parser.add_argument(
        "--qbittorrent-url",
        required=True,
        help="qBittorrent base URL (e.g., http://localhost:8080)",
    )
    parser.add_argument(
        "--qbittorrent-username",
        required=True,
        help="qBittorrent username",
    )
    parser.add_argument(
        "--qbittorrent-password",
        required=True,
        help="qBittorrent password",
    )
    parser.add_argument(
        "--qbittorrent-port",
        type=int,
        help="qBittorrent port",
    )
    parser.add_argument(
        "--insecure", action="store_true", help="Disable TLS certificate verification"
    )
    args = parser.parse_args()

    # Validate that at least one service is specified
    if not (
        (args.sonarr_url and args.sonarr_apikey)
        or (args.radarr_url and args.radarr_apikey)
    ):
        print(
            "Error: Must specify at least one service (Sonarr or Radarr) with URL and API key",
            file=sys.stderr,
        )
        sys.exit(1)

    verify_tls = not args.insecure
    success_count = 0
    total_count = 0

    # Add qBittorrent to Sonarr if specified
    if args.sonarr_url and args.sonarr_apikey:
        total_count += 1
        try:
            add_qbittorrent_to_sonarr(
                sonarr_url=args.sonarr_url,
                sonarr_api_key=args.sonarr_apikey,
                qbittorrent_url=args.qbittorrent_url,
                qbittorrent_username=args.qbittorrent_username,
                qbittorrent_password=args.qbittorrent_password,
                qbittorrent_port=args.qbittorrent_port,
                verify_tls=verify_tls,
            )
            print("✓ qBittorrent added to Sonarr as download client")
            success_count += 1
        except Exception as e:
            print(f"Error adding qBittorrent to Sonarr: {e}", file=sys.stderr)

    # Add qBittorrent to Radarr if specified
    if args.radarr_url and args.radarr_apikey:
        total_count += 1
        try:
            add_qbittorrent_to_radarr(
                radarr_url=args.radarr_url,
                radarr_api_key=args.radarr_apikey,
                qbittorrent_url=args.qbittorrent_url,
                qbittorrent_username=args.qbittorrent_username,
                qbittorrent_password=args.qbittorrent_password,
                qbittorrent_port=args.qbittorrent_port,
                verify_tls=verify_tls,
            )
            print("✓ qBittorrent added to Radarr as download client")
            success_count += 1
        except Exception as e:
            print(f"Error adding qBittorrent to Radarr: {e}", file=sys.stderr)

    if success_count == total_count:
        print(
            f"✓ qBittorrent configured as download client for all {success_count} services!"
        )
    else:
        print(
            f"Warning: qBittorrent configured for {success_count}/{total_count} services",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
