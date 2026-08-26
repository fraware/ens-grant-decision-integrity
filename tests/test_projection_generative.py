"""Deterministic generative checks for projection-v2 pointer/path invariants."""

from __future__ import annotations

import itertools
import random
import string

import pytest

from gdi.projection import ProjectionErrorV2
from gdi.resources import resource_path


def _projection_module():
    import sys

    src = resource_path("projection", "src")
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    import project_v2

    return project_v2


def test_json_pointer_round_trip_generated_tokens() -> None:
    module = _projection_module()
    rng = random.Random(20260826)
    alphabet = string.ascii_letters + string.digits + "~/ _-."
    token_sets: list[list[str]] = [[], [""], ["a/b", "x~y", "plain"]]
    for width in range(1, 8):
        token_sets.append(
            [
                "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 18)))
                for _ in range(width)
            ]
        )
    for tokens in token_sets:
        pointer = module.format_json_pointer(tokens)
        assert module.parse_json_pointer(pointer) == tokens


def test_pointer_escaping_is_injective_for_small_token_set() -> None:
    module = _projection_module()
    tokens = ["", "~", "/", "~/", "a", "a/b", "a~b", "~0", "~1"]
    formatted = {
        tuple(parts): module.format_json_pointer(list(parts))
        for length in range(0, 3)
        for parts in itertools.product(tokens, repeat=length)
    }
    assert len(set(formatted.values())) == len(formatted)


def test_malformed_pointer_escapes_fail_closed() -> None:
    module = _projection_module()
    malformed = ["no-leading-slash", "/~", "/~2", "/abc~9", "/a/~x"]
    for pointer in malformed:
        with pytest.raises(ProjectionErrorV2) as exc:
            module.parse_json_pointer(pointer)
        assert exc.value.code == "PROJ201"


def test_array_index_addressing_fails_closed() -> None:
    module = _projection_module()
    record = {"root": {"items": [{"secret": 1}]}}
    with pytest.raises(ProjectionErrorV2) as exc:
        module.resolve_pointer(record, "/root/items/0/secret")
    assert exc.value.code == "PROJ214"
