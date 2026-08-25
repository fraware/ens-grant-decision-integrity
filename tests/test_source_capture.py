"""SSRF-safe source capture tests (offline; no live network)."""

from __future__ import annotations

from pathlib import Path

import pytest

from gdi.source.artifact import SourceArtifactError
from gdi.source.capture import (
    assert_safe_url,
    capture_http,
    capture_manual_file,
    store_captured_bytes,
)


def test_ssrf_rejects_localhost() -> None:
    with pytest.raises(SourceArtifactError) as exc:
        assert_safe_url("https://localhost/policy", resolver=lambda _h: ["127.0.0.1"])
    assert exc.value.code in {"CAP006", "CAP008"}


def test_ssrf_rejects_link_local() -> None:
    with pytest.raises(SourceArtifactError) as exc:
        assert_safe_url("https://metadata/latest", resolver=lambda _h: ["169.254.169.254"])
    assert exc.value.code in {"CAP006", "CAP008"}


def test_ssrf_rejects_private_rfc1918() -> None:
    with pytest.raises(SourceArtifactError) as exc:
        assert_safe_url("https://intranet.example/policy", resolver=lambda _h: ["10.0.0.5"])
    assert exc.value.code == "CAP008"


def test_ssrf_rejects_file_scheme() -> None:
    with pytest.raises(SourceArtifactError) as exc:
        assert_safe_url("file:///etc/passwd")
    assert exc.value.code == "CAP002"


def test_ssrf_rejects_http_without_allow() -> None:
    with pytest.raises(SourceArtifactError) as exc:
        assert_safe_url("http://example.org/x", resolver=lambda _h: ["93.184.216.34"])
    assert exc.value.code == "CAP004"


def test_redirect_into_private_ip_rejected(tmp_path: Path) -> None:
    class _Headers(dict):
        def get_content_type(self) -> str:
            return "text/plain"

        def get_content_charset(self) -> str | None:
            return None

    class _Resp:
        def __init__(self, status: int, headers: dict[str, str], body: bytes = b"") -> None:
            self.status = status
            self.headers = headers
            self._body = body

        def getcode(self) -> int:
            return self.status

        def read(self, _n: int = -1) -> bytes:
            data, self._body = self._body, b""
            return data

        def __enter__(self) -> "_Resp":
            return self

        def __exit__(self, *args: object) -> None:
            return None

    calls = {"n": 0}

    def opener(request: object, timeout: int = 0) -> _Resp:
        calls["n"] += 1
        if calls["n"] == 1:
            return _Resp(302, _Headers({"Location": "https://evil.internal/secret"}))
        raise AssertionError("second hop should be blocked before open")

    def resolver(host: str) -> list[str]:
        if host == "example.org":
            return ["93.184.216.34"]
        if host == "evil.internal":
            return ["192.168.1.10"]
        return ["8.8.8.8"]

    with pytest.raises(SourceArtifactError) as exc:
        capture_http(
            source_uri="https://example.org/policy",
            out_dir=tmp_path,
            artifact_id="cap-1",
            opener=opener,
            resolver=resolver,
        )
    assert exc.value.code == "CAP008"


def test_manual_file_content_addressed(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    src.write_bytes(b"exact policy bytes\n")
    out = tmp_path / "evidence"
    result = capture_manual_file(
        source_uri="urn:ens-gdi:manual:policy-1",
        file_path=src,
        out_dir=out,
        artifact_id="manual-1",
        media_type="text/plain",
    )
    assert result.bytes_path.is_file()
    assert result.artifact["capture"]["method"] == "manual-file"
    again = store_captured_bytes(
        out_dir=out,
        data=b"exact policy bytes\n",
        artifact_id="manual-2",
        source_uri="urn:ens-gdi:manual:policy-2",
        method="manual-file",
        media_type="text/plain",
    )
    assert again.bytes_path == result.bytes_path


def test_changed_bytes_create_distinct_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "evidence"
    a = store_captured_bytes(
        out_dir=out,
        data=b"v1\n",
        artifact_id="a",
        source_uri="https://example.org/p",
        method="manual-file",
        media_type="text/plain",
    )
    b = store_captured_bytes(
        out_dir=out,
        data=b"v2\n",
        artifact_id="b",
        source_uri="https://example.org/p",
        method="manual-file",
        media_type="text/plain",
    )
    assert a.bytes_path != b.bytes_path
