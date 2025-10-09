#!/usr/bin/env python3
"""
Setup root folders for Sonarr and Radarr via their APIs.

Requirements:
- Python 3.8+
- requests (pip install requests)

Usage examples:
  # Setup root folders for both Sonarr and Radarr
  python setup_root_folders.py \
    --sonarr-url http://localhost:8989 \
    --sonarr-apikey <SONARR_API_KEY> \
    --radarr-url http://localhost:7878 \
    --radarr-apikey <RADARR_API_KEY>

  # Setup only Sonarr root folder
  python setup_root_folders.py \
    --sonarr-url http://localhost:8989 \
    --sonarr-apikey <SONARR_API_KEY>

  # Setup only Radarr root folder
  python setup_root_folders.py \
    --radarr-url http://localhost:7878 \
    --radarr-apikey <RADARR_API_KEY>
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


def _post_json(url: str, headers: dict, payload: dict, verify: bool) -> dict:
    r = requests.post(url, headers=headers, json=payload, timeout=30, verify=verify)
    if r.status_code >= 400:
        raise RuntimeError(f"POST {url} failed: {r.status_code} {r.text}")
    return r.json()


def _get_json(url: str, headers: dict, verify: bool) -> list | dict:
    r = requests.get(url, headers=headers, timeout=15, verify=verify)
    if r.status_code >= 400:
        raise RuntimeError(f"GET {url} failed: {r.status_code} {r.text}")
    return r.json()


def _normalize_base_url(u: str) -> str:
    # Ensure no trailing slash for baseUrl fields
    return u.rstrip("/")


def setup_sonarr_root_folder(
    sonarr_url: str,
    sonarr_api_key: str,
    root_path: str = "/data/tv/",
    verify_tls: bool = True,
) -> dict:
    """Setup root folder for TV shows in Sonarr."""
    sonarr_url = _normalize_base_url(sonarr_url)
    headers = _headers(sonarr_api_key)

    existing = _get_json(
        urljoin(sonarr_url + "/", "api/v3/rootfolder"), headers, verify_tls
    )
    for folder in existing:
        if folder.get("path") == root_path.rstrip("/"):
            return folder

    payload = {
        "path": root_path,
        "accessible": True,
        "freeSpace": 0,
        "unmappedFolders": [],
    }

    create_url = urljoin(sonarr_url + "/", "api/v3/rootfolder")
    created = _post_json(create_url, headers, payload, verify_tls)
    return created


def setup_radarr_root_folder(
    radarr_url: str,
    radarr_api_key: str,
    root_path: str = "/data/movies/",
    verify_tls: bool = True,
) -> dict:
    """Setup root folder for movies in Radarr."""
    radarr_url = _normalize_base_url(radarr_url)
    headers = _headers(radarr_api_key)

    existing = _get_json(
        urljoin(radarr_url + "/", "api/v3/rootfolder"), headers, verify_tls
    )
    for folder in existing:
        if folder.get("path") == root_path.rstrip("/"):
            return folder

    payload = {
        "path": root_path,
        "accessible": True,
        "freeSpace": 0,
        "unmappedFolders": [],
    }

    create_url = urljoin(radarr_url + "/", "api/v3/rootfolder")
    created = _post_json(create_url, headers, payload, verify_tls)
    return created


def main():
    parser = argparse.ArgumentParser(
        description="Setup root folders for Sonarr and Radarr."
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
        "--tv-path",
        default="/data/tv/",
        help="TV shows root folder path (default: /data/tv/)",
    )
    parser.add_argument(
        "--movies-path",
        default="/data/movies/",
        help="Movies root folder path (default: /data/movies/)",
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

    # Setup Sonarr root folder if specified
    if args.sonarr_url and args.sonarr_apikey:
        total_count += 1
        try:
            created = setup_sonarr_root_folder(
                sonarr_url=args.sonarr_url,
                sonarr_api_key=args.sonarr_apikey,
                root_path=args.tv_path,
                verify_tls=verify_tls,
            )
            print(f"✓ TV root folder added to Sonarr: {created.get('path')}")
            success_count += 1
        except Exception as e:
            print(f"Error adding TV root folder to Sonarr: {e}", file=sys.stderr)

    # Setup Radarr root folder if specified
    if args.radarr_url and args.radarr_apikey:
        total_count += 1
        try:
            created = setup_radarr_root_folder(
                radarr_url=args.radarr_url,
                radarr_api_key=args.radarr_apikey,
                root_path=args.movies_path,
                verify_tls=verify_tls,
            )
            print(f"✓ Movies root folder added to Radarr: {created.get('path')}")
            success_count += 1
        except Exception as e:
            print(f"Error adding Movies root folder to Radarr: {e}", file=sys.stderr)

    if success_count == total_count:
        print(f"✓ All {success_count} root folders configured successfully!")
    else:
        print(
            f"Warning: {success_count}/{total_count} root folders configured successfully",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
