"""T1: RFC 8785 vectors and two independent implementations produce identical bytes."""

from __future__ import annotations

import json
from pathlib import Path

import jcs
import rfc8785

from canonicalize import canonicalize

VECTORS = Path(__file__).resolve().parents[1] / "vectors"


def _second(value: object) -> bytes:
    encoded = jcs.canonicalize(value)
    return encoded if isinstance(encoded, (bytes, bytearray)) else encoded.encode("utf-8")


def test_rfc8785_section_322_literals_and_numbers() -> None:
    parsed = json.loads(
        '{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],'
        '"string":"\\u20ac$\\u000f\\nA\'B\\"\\\\\\\\\\"/",'
        '"literals":[null,true,false]}'
    )
    production = canonicalize(parsed)
    second = _second(parsed)
    library = rfc8785.dumps(parsed)
    library_bytes = bytes(library) if isinstance(library, (bytes, bytearray)) else library.encode("utf-8")
    assert production == second == library_bytes
    text = production.decode("utf-8")
    assert text.index('"literals"') < text.index('"numbers"') < text.index('"string"')
    assert "4.5" in text
    assert "0.002" in text
    vector_path = VECTORS / "t1_rfc8785_section_322.jcs.txt"
    if vector_path.is_file():
        expected = vector_path.read_bytes().replace(b"\r\n", b"\n").strip()
        assert production == expected


def test_independent_implementations_key_order_and_unicode() -> None:
    value = {
        "b": True,
        "a": [None, {"z": "café", "y": 1}],
        "c": "line\nbreak",
    }
    production = canonicalize(value)
    second = _second(value)
    assert production == second
    assert production.startswith(b"{")
    assert b'"a":' in production
    # RFC 8785 lexicographic key order places "a" before "b" before "c".
    assert production.index(b'"a"') < production.index(b'"b"') < production.index(b'"c"')


def test_vector_file_objects_match_both_implementations() -> None:
    objects = json.loads((VECTORS / "t1_objects.json").read_text(encoding="utf-8"))
    for item in objects:
        value = item["value"]
        production = canonicalize(value)
        second = _second(value)
        assert production == second
        if item.get("jcsUtf8Hex"):
            assert production.hex() == item["jcsUtf8Hex"]
