"""Salted, domain-separated SHA-256 commitment over JCS(manifest)."""

from __future__ import annotations

import secrets
from typing import Any

from canonicalize import canonicalize
from claims import COMMITMENT_DOMAIN
from support import Phase2Error, sha256_hex

SALT_SIZE = 32
DOMAIN_SEPARATOR = COMMITMENT_DOMAIN.encode("utf-8") + b"\x00"


def generate_salt() -> bytes:
    return secrets.token_bytes(SALT_SIZE)


def domain_bytes(domain: str = COMMITMENT_DOMAIN) -> bytes:
    return domain.encode("utf-8") + b"\x00"


def commitment_digest(
    manifest: Any,
    salt: bytes,
    *,
    domain: str = COMMITMENT_DOMAIN,
) -> str:
    if not isinstance(salt, (bytes, bytearray)) or len(salt) != SALT_SIZE:
        raise Phase2Error("salt must be 32 bytes", code="CMT001")
    canonical = canonicalize(manifest)
    digest = sha256_hex(domain_bytes(domain) + bytes(salt) + canonical)
    return digest


def open_commitment(
    *,
    digest_hex: str,
    manifest: Any,
    salt: bytes,
    domain: str = COMMITMENT_DOMAIN,
) -> None:
    expected = commitment_digest(manifest, salt, domain=domain)
    if expected != digest_hex.lower():
        raise Phase2Error(
            "revealed manifest and salt do not reopen the digest",
            code="CMT002",
            claim="C1",
        )
