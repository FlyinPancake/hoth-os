#!/usr/bin/env python3
import os
import base64
import hashlib
import hmac


ITERATIONS = 100_000
DKLEN = 64  # bytes
HASH_NAME = "sha512"
SALT_LEN = 16  # bytes


def generate(password: str) -> str:
    """
    Generate a qBittorrent-compatible password hash string:
    base64(salt) + ":" + base64(PBKDF2-HMAC-SHA512(password, salt, 100000, 64))
    """
    salt = os.urandom(SALT_LEN)
    dk = hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode("utf-8"), salt, ITERATIONS, dklen=DKLEN
    )
    return f"{base64.b64encode(salt).decode()}:{base64.b64encode(dk).decode()}"


def verify(secret: str, password: str) -> bool:
    """
    Verify a password against a qBittorrent-compatible secret string.
    """
    try:
        salt_b64, key_b64 = secret.split(":", 1)
        salt = base64.b64decode(salt_b64)
        expected_key = base64.b64decode(key_b64)
    except Exception:
        return False

    dk = hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode("utf-8"), salt, ITERATIONS, dklen=DKLEN
    )
    return hmac.compare_digest(dk, expected_key)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="qBittorrent PBKDF2-HMAC-SHA512 password hash generator/verifier"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate a hash for a password")
    g.add_argument("password", help="Password (will be encoded as UTF-8)")

    v = sub.add_parser("verify", help="Verify a password against a hash")
    v.add_argument(
        "secret", help='Hash string in the form "base64(salt):base64(derived_key)"'
    )
    v.add_argument("password", help="Password to verify")

    args = ap.parse_args()
    if args.cmd == "generate":
        print(generate(args.password))
    elif args.cmd == "verify":
        ok = verify(args.secret, args.password)
        print("OK" if ok else "FAIL")
