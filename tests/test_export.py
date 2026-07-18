from pathlib import Path

from social_rv_research.export import (
    ext_from_mime,
    load_done_set,
    make_headers,
    save_done_set,
)


def test_make_headers_uses_research_api_header() -> None:
    assert make_headers("secret") == {"X-API-Key": "secret"}


def test_extension_normalizes_jpeg() -> None:
    assert ext_from_mime("image/jpeg") == ".jpg"


def test_progress_round_trip(tmp_path: Path) -> None:
    progress_file = tmp_path / ".progress" / "sessions_done.json"

    save_done_set(progress_file, {"session-1", "session-2"})

    assert load_done_set(progress_file) == {"session-1", "session-2"}


def test_invalid_progress_is_treated_as_empty(tmp_path: Path) -> None:
    progress_file = tmp_path / "broken.json"
    progress_file.write_text("{", encoding="utf-8")

    assert load_done_set(progress_file) == set()
