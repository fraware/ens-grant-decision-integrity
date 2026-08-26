from __future__ import annotations

from pathlib import Path

import pytest

from cli import _load_json, main
from support import Phase2Error


def test_phase2_loader_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"bundleVersion":"2","bundleVersion":"1"}\n', encoding="utf-8")

    with pytest.raises(Phase2Error) as exc:
        _load_json(str(path))
    assert exc.value.code == "CLI012"
    assert "duplicate JSON object key" in str(exc.value)


def test_phase2_cli_rejects_nonstandard_nan_without_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "manifest.json"
    path.write_text('{"score": NaN}\n', encoding="utf-8")

    code = main(
        [
            "commit",
            "--manifest",
            str(path),
            "--out-envelope",
            str(tmp_path / "envelope.json"),
            "--out-salt",
            str(tmp_path / "salt.json"),
        ]
    )
    output = capsys.readouterr().out
    assert code == 1
    assert '"code": "CLI012"' in output
    assert "non-standard JSON numeric constant" in output
