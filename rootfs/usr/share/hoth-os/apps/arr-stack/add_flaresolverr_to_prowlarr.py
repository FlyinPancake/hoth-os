#!/usr/bin/env python3
"""
Add FlareSolverr as an indexer proxy to Prowlarr via Prowlarr's API.

Requirements:
- Python 3.8+
- requests (pip install requests)

Usage example:
  python add_flaresolverr_to_prowlarr.py \
    --prowlarr-url http://localhost:9696 \
    --prowlarr-apikey <PROWLARR_API_KEY> \
    --flaresolverr-url http://localhost:8191
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


def _pick_schema(schemas: list, implementation: str) -> dict | None:
    # Look for implementation match (e.g., "FlareSolverr")
    for s in schemas:
        if s.get("implementation") == implementation:
            return s
    return None


def _find_field(fields: list, name: str) -> dict | None:
    lname = name.lower()
    for f in fields:
        if f.get("name", "").lower() == lname:
            return f
    return None


def add_flaresolverr_to_prowlarr(
    prowlarr_url: str,
    prowlarr_api_key: str,
    flaresolverr_url: str,
    name: str = "FlareSolverr",
    verify_tls: bool = True,
) -> dict:
    prowlarr_url = _normalize_base_url(prowlarr_url)
    flaresolverr_url = _normalize_base_url(flaresolverr_url)
    headers = _headers(prowlarr_api_key)

    # 1) Discover available indexer proxy schemas
    schema_url = urljoin(prowlarr_url + "/", "api/v1/indexerproxy/schema")
    schemas = _get_json(schema_url, headers, verify_tls)
    if not isinstance(schemas, list) or not schemas:
        raise RuntimeError("No indexer proxy schemas returned by Prowlarr.")

    # Look for FlareSolverr schema
    schema = _pick_schema(schemas, "FlareSolverr")
    if not schema:
        raise RuntimeError("FlareSolverr implementation not found in Prowlarr schemas.")

    # 2) Prepare fields from schema, overriding host field
    fields = schema.get("fields", []) or []

    # Set the host field to the FlareSolverr URL
    host_field = _find_field(fields, "host")
    if not host_field:
        host_field = {"name": "host"}
        fields.append(host_field)
    host_field["value"] = flaresolverr_url

    # 3) Build payload for indexer proxy
    payload = {
        "name": name,
        "enable": True,
        "implementationName": schema.get("implementationName", "FlareSolverr"),
        "implementation": schema.get("implementation", "FlareSolverr"),
        "configContract": schema.get("configContract"),
        "tags": [],
        "fields": fields,
    }

    # 4) Create the indexer proxy
    create_url = urljoin(prowlarr_url + "/", "api/v1/indexerproxy")
    created = _post_json(create_url, headers, payload, verify_tls)
    return created


def main():
    parser = argparse.ArgumentParser(
        description="Add FlareSolverr as an indexer proxy to Prowlarr."
    )
    parser.add_argument(
        "--prowlarr-url",
        required=True,
        help="Prowlarr base URL (e.g., http://localhost:9696)",
    )
    parser.add_argument("--prowlarr-apikey", required=True, help="Prowlarr API key")
    parser.add_argument(
        "--flaresolverr-url",
        default="http://localhost:8191",
        help="FlareSolverr base URL (default: http://localhost:8191)",
    )
    parser.add_argument(
        "--name",
        default="FlareSolverr",
        help="Display name in Prowlarr (default: FlareSolverr)",
    )
    parser.add_argument(
        "--insecure", action="store_true", help="Disable TLS certificate verification"
    )
    args = parser.parse_args()

    try:
        result = add_flaresolverr_to_prowlarr(
            prowlarr_url=args.prowlarr_url,
            prowlarr_api_key=args.prowlarr_apikey,
            flaresolverr_url=args.flaresolverr_url,
            name=args.name,
            verify_tls=not args.insecure,
        )
        print("Successfully added FlareSolverr to Prowlarr")
        print(f"Proxy ID: {result.get('id')}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
