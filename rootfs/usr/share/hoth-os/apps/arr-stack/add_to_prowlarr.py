#!/usr/bin/env python3
"""
Add a Sonarr or Radarr application to Prowlarr via Prowlarr's API.

Requirements:
- Python 3.8+
- requests (pip install requests)

Usage examples:
  # Add a Sonarr running on localhost:8989
  python add_arr_to_prowlarr.py \
    --prowlarr-url http://localhost:9696 \
    --prowlarr-apikey <PROWLARR_API_KEY> \
    --arr-type sonarr \
    --port 8989 \
    --arr-apikey <SONARR_API_KEY>

  # Add a Radarr running on a custom URL
  python add_arr_to_prowlarr.py \
    --prowlarr-url http://localhost:9696 \
    --prowlarr-apikey <PROWLARR_API_KEY> \
    --arr-type radarr \
    --arr-url http://localhost:7878 \
    --arr-apikey <RADARR_API_KEY>
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
    # Look for implementation match (e.g., "Sonarr" or "Radarr")
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


def _get_default_app_profile_id(
    prowlarr_url: str, headers: dict, verify: bool
) -> int | None:
    # Try to get App Profiles (endpoint name is appprofile in Prowlarr)
    try:
        profiles_url = urljoin(
            prowlarr_url if prowlarr_url.endswith("/") else prowlarr_url + "/",
            "api/v1/appprofile",
        )
        profiles = _get_json(profiles_url, headers, verify)
        if isinstance(profiles, list) and profiles:
            # Prefer "Default" if present
            for p in profiles:
                if p.get("name", "").lower() == "default":
                    return p.get("id")
            # Fallback to the first profile
            return profiles[0].get("id")
    except Exception:
        # If profiles cannot be fetched, silently fall back to None (Prowlarr may choose a default)
        return None
    return None


def add_app_to_prowlarr(
    prowlarr_url: str,
    prowlarr_api_key: str,
    arr_type: str,
    arr_url: str,
    arr_api_key: str,
    name: str,
    verify_tls: bool = True,
) -> dict:
    prowlarr_url = _normalize_base_url(prowlarr_url)
    arr_url = _normalize_base_url(arr_url)
    headers = _headers(prowlarr_api_key)

    # 1) Discover available application schemas
    schema_url = urljoin(prowlarr_url + "/", "api/v1/applications/schema")
    schemas = _get_json(schema_url, headers, verify_tls)
    if not isinstance(schemas, list) or not schemas:
        raise RuntimeError("No application schemas returned by Prowlarr.")

    impl_map = {"sonarr": "Sonarr", "radarr": "Radarr"}
    impl = impl_map[arr_type.lower()]
    schema = _pick_schema(schemas, impl)
    if not schema:
        raise RuntimeError(f"Implementation '{impl}' not found in Prowlarr schemas.")

    # 2) Prepare fields from schema, overriding baseUrl and apiKey
    # The schema typically includes a 'fields' list where each field has a 'name' and default values.
    fields = schema.get("fields", []) or []

    # Ensure baseUrl field exists (create if missing)
    base_url_field = _find_field(fields, "baseUrl")
    if not base_url_field:
        base_url_field = {"name": "baseUrl"}
        fields.append(base_url_field)
    base_url_field["value"] = arr_url

    # Ensure apiKey field exists (create if missing)
    api_key_field = _find_field(fields, "apiKey")
    if not api_key_field:
        api_key_field = {"name": "apiKey"}
        fields.append(api_key_field)
    api_key_field["value"] = arr_api_key

    # Optional: some schemas support urlBase or additional fields; leave schema defaults unless user specifies.

    # 3) Pick an app profile if available
    app_profile_id = _get_default_app_profile_id(prowlarr_url, headers, verify_tls)

    # 4) Build payload. Many *arr APIs expect these top-level fields for provider definitions.
    payload = {
        "name": name or f"Local {impl}",
        "enable": True,
        "implementationName": schema.get("implementationName", impl),
        "implementation": schema.get("implementation", impl),
        "configContract": schema.get("configContract"),
        "tags": [],
        "fields": fields,
    }

    if app_profile_id is not None:
        payload["appProfileId"] = app_profile_id

    # 5) Create the application
    create_url = urljoin(prowlarr_url + "/", "api/v1/applications")
    created = _post_json(create_url, headers, payload, verify_tls)
    return created


def main():
    parser = argparse.ArgumentParser(
        description="Add a Sonarr or Radarr application to Prowlarr."
    )
    parser.add_argument(
        "--prowlarr-url",
        required=True,
        help="Prowlarr base URL (e.g., http://localhost:9696)",
    )
    parser.add_argument("--prowlarr-apikey", required=True, help="Prowlarr API key")
    parser.add_argument(
        "--arr-type",
        required=True,
        choices=["sonarr", "radarr"],
        help="Target application type to add to Prowlarr",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--port",
        type=int,
        help="Port of the Sonarr/Radarr instance on localhost (e.g., 8989 or 7878)",
    )
    group.add_argument(
        "--arr-url",
        help="Full base URL of the Sonarr/Radarr instance (e.g., http://localhost:8989)",
    )
    parser.add_argument(
        "--arr-apikey", required=True, help="API key of the Sonarr/Radarr instance"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Display name in Prowlarr (default: Local Sonarr/Radarr)",
    )
    parser.add_argument(
        "--insecure", action="store_true", help="Disable TLS certificate verification"
    )
    args = parser.parse_args()

    arr_url = args.arr_url or f"http://localhost:{args.port}"

    try:
        created = add_app_to_prowlarr(
            prowlarr_url=args.prowlarr_url,
            prowlarr_api_key=args.prowlarr_apikey,
            arr_type=args.arr_type,
            arr_url=arr_url,
            arr_api_key=args.arr_apikey,
            name=args.name,
            verify_tls=not args.insecure,
        )
        print("Successfully added application to Prowlarr:")
        print(created)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
