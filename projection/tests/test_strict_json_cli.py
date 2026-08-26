from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cli import main  # noqa: E402
from gdi.jsonutil import StrictJSONError  # noqa: E402
from project import load_json as load_json_v1  # noqa: E402
from project_v2 import load_json as load_json_v2  # noqa: E402


@pytest.mark.parametrize("loader", [load_json_v1, load_json_v2])
def test_projection_loaders_reject_duplicate_json_keys(tmp_path: Path, loader: object) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"specVersion":"2","specVersion":"1"}\n', encoding="utf-8")

    with pytest.raises(StrictJSONError, match="duplicate JSON object key"):
        loader(path)  # type: ignore[operator]


def test_projection_cli_rejects_nonstandard_nan_without_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    confidential = tmp_path / "confidential.json"
    confidential.write_text('{"recordId":"x","requestedAmount":NaN}\n', encoding="utf-8")

    code = main(
        [
            "project",
            "--confidential",
            str(confidential),
            "--spec",
            str(tmp_path / "unused-spec.json"),
            "--out",
            str(tmp_path / "public.json"),
        ]
    )
    output = capsys.readouterr().out
    assert code == 1
    assert "non-standard JSON numeric constant" in output
