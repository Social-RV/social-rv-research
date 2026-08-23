from pathlib import Path

from social_rv_research.export import (
    ext_from_mime,
    flatten_session,
    json_cell,
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


def test_json_cell_serializes_objects_and_blanks_empty() -> None:
    assert json_cell({"preset": "gpt5mini_all_in_one", "model": "gpt-5-mini"}) == (
        '{"preset":"gpt5mini_all_in_one","model":"gpt-5-mini"}'
    )
    assert json_cell({}) == ""
    assert json_cell(None) == ""
    assert json_cell("not-an-object") == ""


def test_flatten_session_includes_judge_metadata() -> None:
    row = flatten_session(
        {
            "id": "session-1",
            "user": {"user_id": "user-1", "display_name": "viewer1"},
            "community_score": {"average": 4.5, "num_scores": 2},
            "targetData": {"targetId": "target-1", "description": "A waterfall"},
            "ai_judging": {
                "decoy": {
                    "rank": 2,
                    "judge_version": "decoy_judge_v2",
                    "description": "Falling water",
                    "decoy_target_ids": ["a", "b"],
                    "judge_metadata": {
                        "preset": "gpt5mini_all_in_one",
                        "model": "gpt-5-mini-2025-08-07",
                    },
                },
                "decoy_legacy": {
                    "rank": 5,
                    "judge_version": "legacy",
                    "judge_metadata": {},
                },
                "targ": {
                    "score": 4,
                    "analysis": "Some match",
                    "judge_metadata": {"preset": "gpt56luna_standard"},
                },
            },
        }
    )

    assert row["decoy_rank"] == 2
    assert row["decoy_judge_metadata"] == (
        '{"preset":"gpt5mini_all_in_one","model":"gpt-5-mini-2025-08-07"}'
    )
    assert row["decoy_legacy_rank"] == 5
    assert row["decoy_legacy_judge_metadata"] == ""
    assert row["targ_score"] == 4
    assert row["targ_judge_metadata"] == '{"preset":"gpt56luna_standard"}'
