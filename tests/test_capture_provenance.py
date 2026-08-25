"""Capture provenance must not collapse merely because bytes are identical."""

from __future__ import annotations

from pathlib import Path

import pytest

from gdi.source.artifact import SourceArtifactError
from gdi.source.capture import store_captured_bytes


def test_same_content_different_artifacts_share_bytes_not_metadata(tmp_path: Path) -> None:
    out = tmp_path / "evidence"
    first = store_captured_bytes(
        out_dir=out,
        data=b"same bytes\n",
        artifact_id="capture-a",
        source_uri="https://example.org/a",
        method="manual-file",
        media_type="text/plain",
    )
    second = store_captured_bytes(
        out_dir=out,
        data=b"same bytes\n",
        artifact_id="capture-b",
        source_uri="https://example.org/b",
        method="manual-file",
        media_type="text/plain",
    )
    assert first.bytes_path == second.bytes_path
    assert first.artifact_path != second.artifact_path
    assert first.capture_log_path != second.capture_log_path
    assert first.artifact["artifactId"] == "capture-a"
    assert second.artifact["artifactId"] == "capture-b"


def test_artifact_id_cannot_silently_overwrite_prior_capture(tmp_path: Path) -> None:
    out = tmp_path / "evidence"
    store_captured_bytes(
        out_dir=out,
        data=b"v1\n",
        artifact_id="unique-capture",
        source_uri="https://example.org/a",
        method="manual-file",
        media_type="text/plain",
    )
    with pytest.raises(SourceArtifactError) as exc:
        store_captured_bytes(
            out_dir=out,
            data=b"v2\n",
            artifact_id="unique-capture",
            source_uri="https://example.org/a",
            method="manual-file",
            media_type="text/plain",
        )
    assert exc.value.code == "CAP020"
