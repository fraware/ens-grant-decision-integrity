"""in-toto Statement v1 + DSSE run attestation with a custom predicate."""

from __future__ import annotations

import base64
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from canonicalize import canonicalize
from claims import DSSE_PAYLOAD_TYPE, IN_TOTO_STATEMENT_TYPE, PREDICATE_TYPE
from support import Phase2Error, sha256_hex, validate_schema


def dsse_pae(payload_type: str, payload: bytes) -> bytes:
    type_bytes = payload_type.encode("utf-8")
    return (
        b"DSSEv1 "
        + str(len(type_bytes)).encode("ascii")
        + b" "
        + type_bytes
        + b" "
        + str(len(payload)).encode("ascii")
        + b" "
        + payload
    )


def generate_test_ed25519() -> tuple[bytes, bytes]:
    key = Ed25519PrivateKey.generate()
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def load_ed25519_private(pem: str | bytes) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(
        pem.encode("utf-8") if isinstance(pem, str) else pem,
        password=None,
    )
    if not isinstance(key, Ed25519PrivateKey):
        raise Phase2Error("run attestation key must be Ed25519", code="ATT001")
    return key


def load_ed25519_public(pem: str | bytes) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(pem.encode("utf-8") if isinstance(pem, str) else pem)
    if not isinstance(key, Ed25519PublicKey):
        raise Phase2Error("run attestation public key must be Ed25519", code="ATT002")
    return key


def build_statement(predicate: dict[str, Any]) -> dict[str, Any]:
    validate_schema(predicate, "run-predicate.schema.json")
    statement = {
        "_type": IN_TOTO_STATEMENT_TYPE,
        "subject": [
            {
                "name": "evaluator-run-output",
                "digest": {"sha256": predicate["outputDigest"]},
            }
        ],
        "predicateType": PREDICATE_TYPE,
        "predicate": predicate,
    }
    return statement


def attest_run(predicate: dict[str, Any], private_key: Ed25519PrivateKey) -> dict[str, Any]:
    statement = build_statement(predicate)
    payload = canonicalize(statement)
    pae = dsse_pae(DSSE_PAYLOAD_TYPE, payload)
    signature = private_key.sign(pae)
    public_der = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    envelope = {
        "payload": base64.b64encode(payload).decode("ascii"),
        "payloadType": DSSE_PAYLOAD_TYPE,
        "signatures": [
            {
                "keyid": sha256_hex(public_der),
                "sig": base64.b64encode(signature).decode("ascii"),
            }
        ],
    }
    return envelope


def verify_run(envelope: dict[str, Any], public_key: Ed25519PublicKey) -> dict[str, Any]:
    if envelope.get("payloadType") != DSSE_PAYLOAD_TYPE:
        raise Phase2Error("unexpected DSSE payload type", code="ATT003", claim="C4")
    payload = base64.b64decode(envelope["payload"])
    signatures = envelope.get("signatures") or []
    if not signatures:
        raise Phase2Error("DSSE envelope has no signatures", code="ATT004", claim="C4")
    pae = dsse_pae(DSSE_PAYLOAD_TYPE, payload)
    verified = False
    for item in signatures:
        try:
            public_key.verify(base64.b64decode(item["sig"]), pae)
            verified = True
            break
        except InvalidSignature:
            continue
    if not verified:
        raise Phase2Error("run attestation signature is invalid", code="ATT005", claim="C4")
    statement = json_loads_utf8(payload)
    if statement.get("_type") != IN_TOTO_STATEMENT_TYPE:
        raise Phase2Error("attestation is not an in-toto Statement v1", code="ATT006", claim="C4")
    if statement.get("predicateType") != PREDICATE_TYPE:
        raise Phase2Error("attestation predicateType is not the Phase II evaluator-run predicate", code="ATT007", claim="C4")
    predicate = statement["predicate"]
    validate_schema(predicate, "run-predicate.schema.json")
    subjects = statement.get("subject") or []
    if not subjects or subjects[0].get("digest", {}).get("sha256") != predicate["outputDigest"]:
        raise Phase2Error("in-toto subject digest does not match predicate outputDigest", code="ATT008", claim="C4")
    return statement


def json_loads_utf8(payload: bytes) -> dict[str, Any]:
    import json

    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise Phase2Error("attestation payload is not a JSON object", code="ATT009", claim="C4")
    return value
