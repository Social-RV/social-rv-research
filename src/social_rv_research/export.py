#!/usr/bin/env python3
"""
Social RV Research Data Export CLI

Downloads targets and sessions from the Social RV research API into a structured
folder layout with CSV metadata files and media files organized by ID.

Usage:
    python research_export.py --api-key KEY pull-targets [--limit N] [--parallel N]
    python research_export.py --api-key KEY pull-sessions [--limit N] [--parallel N]

Environment variables:
    RESEARCH_API_KEY    API key (alternative to --api-key)
    RESEARCH_BASE_URL   Base URL (alternative to --base-url)
"""

import csv
import json
import mimetypes
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import click
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://social-rv.com"
DEFAULT_PARALLEL = 8
DEFAULT_PAGE_SIZE = 100
REQUEST_TIMEOUT = 60
INTER_PAGE_SLEEP = 0.1  # seconds between page fetches


# ---------------------------------------------------------------------------
# Progress tracking helpers
# ---------------------------------------------------------------------------


def load_done_set(progress_file: Path) -> set[str]:
    """Load a set of completed IDs from a JSON progress file."""
    if progress_file.exists():
        try:
            with open(progress_file) as f:
                data = json.load(f)
                return set(data)
        except (json.JSONDecodeError, TypeError):
            return set()
    return set()


def save_done_set(progress_file: Path, done: set[str]) -> None:
    """Persist the done set to disk atomically."""
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = progress_file.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(list(done), f)
    tmp.replace(progress_file)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def make_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key}


def fetch_page(base_url: str, api_key: str, path: str, params: dict) -> dict:
    """Fetch a single API page. Raises on non-2xx responses."""
    url = f"{base_url.rstrip('/')}{path}"
    resp = requests.get(url, headers=make_headers(api_key), params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def fetch_all_pages(
    base_url: str,
    api_key: str,
    path: str,
    extra_params: dict,
    result_key: str,
    limit: Optional[int] = None,
) -> tuple[list[dict], dict]:
    """
    Paginate through all pages of an API endpoint.

    Returns (all_items, first_page_body) — the first page body carries
    top-level metadata like opt_out_summary.
    """
    all_items: list[dict] = []
    first_page_body: dict = {}
    page = 1

    click.echo(f"Fetching metadata from {path} ...")

    while True:
        params = {"page": page, "page_size": DEFAULT_PAGE_SIZE, **extra_params}

        try:
            data = fetch_page(base_url, api_key, path, params)
        except requests.HTTPError as e:
            click.echo(f"  ERROR fetching page {page}: {e}", err=True)
            break
        except requests.RequestException as e:
            click.echo(f"  ERROR fetching page {page}: {e}", err=True)
            break

        if page == 1:
            first_page_body = data

        items = data.get(result_key, [])
        total_pages = data.get("total_pages", 1)
        total_count = data.get("total_count", 0)

        all_items.extend(items)

        click.echo(
            f"  Page {page}/{total_pages} — {len(all_items)}/{total_count} fetched"
        )

        if limit and len(all_items) >= limit:
            all_items = all_items[:limit]
            click.echo(f"  Reached --limit {limit}")
            break

        if page >= total_pages:
            break

        page += 1
        time.sleep(INTER_PAGE_SLEEP)

    click.echo(f"  Done — {len(all_items)} items fetched")
    return all_items, first_page_body


def write_opt_out_summary(output_dir: Path, page_body: dict) -> None:
    """
    Persist the API's data-completeness summary (users who opted out of
    research sharing and how many sessions are excluded because of it).
    """
    summary = page_body.get("opt_out_summary")
    if not summary:
        return
    path = output_dir / "opt_out_summary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    click.echo(f"\nData completeness: {summary.get('note', '')}")
    click.echo(f"  Wrote {path}")


def download_file(url: str, dest: Path, session: requests.Session) -> bool:
    """
    Download a URL to dest. Returns True on success, False on failure.
    Does NOT overwrite if dest already has content (size > 0).
    """
    if dest.exists() and dest.stat().st_size > 0:
        return True  # already present and non-empty

    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
        # Verify we wrote something
        if dest.stat().st_size == 0:
            dest.unlink(missing_ok=True)
            return False
        return True
    except Exception as e:
        click.echo(f"  WARN: failed to download {url}: {e}", err=True)
        dest.unlink(missing_ok=True)
        return False


def ext_from_mime(mime_type: str) -> str:
    """Return a file extension (with dot) for a given MIME type."""
    ext = mimetypes.guess_extension(mime_type)
    if ext:
        # mimetypes sometimes returns .jpe for image/jpeg
        if ext == ".jpe":
            return ".jpg"
        return ext
    # Fallbacks
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "application/pdf": ".pdf",
    }
    return mapping.get(mime_type.lower(), ".bin")


def ext_from_url(url: str) -> str:
    """Guess extension from the URL path."""
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext if ext else ".jpg"


# ---------------------------------------------------------------------------
# CSV writers
# ---------------------------------------------------------------------------


TARGETS_CSV_FIELDS = [
    "id",
    "coordinate",
    "description",
    "pool_name",
    "target_pool_id",
    "created_at",
    "ai_caption",
]

SESSIONS_CSV_FIELDS = [
    "id",
    "user_id",
    "user_display_name",
    "tasking_time",
    "submission_time",
    "target_coordinate",
    "tasking_type",
    "weekly_target_id",
    "group_session_id",
    "is_unrevealed_group_session",
    "is_public",
    "is_low_value",
    "is_highlighted",
    "is_blockchain_verified",
    "self_score",
    "community_score_avg",
    "community_score_count",
    "decoy_rank",
    "decoy_judge_version",
    "decoy_description",
    "decoy_legacy_rank",
    "targ_score",
    "targ_analysis",
    "session_text",
    "num_comments",
    "decoy_ids",
    "target_id",
    "target_description",
]

USERS_CSV_FIELDS = [
    "id",
    "display_name",
    "num_sessions",
    "estimated_start_date",
    "estimated_off_platform_sessions",
]


def flatten_target(t: dict) -> dict:
    return {f: t.get(f) for f in TARGETS_CSV_FIELDS}


def flatten_session(s: dict) -> dict:
    community = s.get("community_score") or {}
    target_data = s.get("targetData") or {}
    user = s.get("user") or {}
    judging = s.get("ai_judging") or {}
    decoy = judging.get("decoy") or {}
    decoy_legacy = judging.get("decoy_legacy") or {}
    targ = judging.get("targ") or {}
    decoys = decoy.get("decoy_target_ids") or []

    return {
        "id": s.get("id"),
        "user_id": user.get("user_id"),
        "user_display_name": user.get("display_name"),
        "tasking_time": s.get("tasking_time"),
        "submission_time": s.get("submission_time"),
        "target_coordinate": s.get("target_coordinate"),
        "tasking_type": s.get("tasking_type"),
        "weekly_target_id": s.get("weekly_target_id"),
        "group_session_id": s.get("group_session_id"),
        "is_unrevealed_group_session": s.get("is_unrevealed_group_session"),
        "is_public": s.get("is_public"),
        "is_low_value": s.get("is_low_value"),
        "is_highlighted": s.get("is_highlighted"),
        "is_blockchain_verified": s.get("is_blockchain_verified"),
        "self_score": s.get("self_score"),
        "community_score_avg": community.get("average"),
        "community_score_count": community.get("num_scores"),
        "decoy_rank": decoy.get("rank"),
        "decoy_judge_version": decoy.get("judge_version"),
        "decoy_description": decoy.get("description"),
        "decoy_legacy_rank": decoy_legacy.get("rank"),
        "targ_score": targ.get("score"),
        "targ_analysis": targ.get("analysis"),
        "session_text": s.get("session_text"),
        "num_comments": s.get("num_comments"),
        "decoy_ids": ",".join(decoys) if decoys else "",
        "target_id": target_data.get("targetId"),
        "target_description": target_data.get("description"),
    }


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    click.echo(f"  Wrote {len(rows)} rows → {path}")


# ---------------------------------------------------------------------------
# CLI definition
# ---------------------------------------------------------------------------


@click.group()
@click.option(
    "--api-key",
    envvar="RESEARCH_API_KEY",
    required=True,
    help="Researcher API key (or set RESEARCH_API_KEY env var)",
)
@click.option(
    "--base-url",
    envvar="RESEARCH_BASE_URL",
    default=DEFAULT_BASE_URL,
    show_default=True,
    help="Base URL of the Social RV API",
)
@click.option(
    "--output-dir",
    default="./research_export",
    show_default=True,
    type=click.Path(),
    help="Root output directory",
)
@click.pass_context
def cli(ctx: click.Context, api_key: str, base_url: str, output_dir: str) -> None:
    """Social RV research data export tool."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url
    ctx.obj["output_dir"] = Path(output_dir)
    ctx.obj["output_dir"].mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# pull-targets command
# ---------------------------------------------------------------------------


@cli.command("pull-targets")
@click.option("--limit", default=None, type=int, help="Max number of targets to process")
@click.option(
    "--parallel",
    default=DEFAULT_PARALLEL,
    show_default=True,
    type=int,
    help="Concurrent image downloads",
)
@click.pass_context
def pull_targets(ctx: click.Context, limit: Optional[int], parallel: int) -> None:
    """Download all targets: images into targets/ and metadata into targets.csv."""
    obj = ctx.obj
    api_key: str = obj["api_key"]
    base_url: str = obj["base_url"]
    output_dir: Path = obj["output_dir"]

    targets_dir = output_dir / "targets"
    targets_dir.mkdir(parents=True, exist_ok=True)
    progress_file = output_dir / ".progress" / "targets_done.json"
    done = load_done_set(progress_file)

    # --- 1. Fetch all target metadata ---
    targets, _ = fetch_all_pages(
        base_url,
        api_key,
        "/api/research/targets",
        {"sort_key": "created_at", "sort_direction": "asc"},
        "targets",
        limit=limit,
    )

    if not targets:
        click.echo("No targets found.")
        return

    # --- 2. Write targets.csv ---
    csv_path = output_dir / "targets.csv"
    write_csv(csv_path, TARGETS_CSV_FIELDS, [flatten_target(t) for t in targets])

    # --- 3. Download images ---
    targets_with_image = [t for t in targets if t.get("imageUrl")]
    to_download = [t for t in targets_with_image if t["id"] not in done]
    already_complete = len(targets_with_image) - len(to_download)

    click.echo(
        f"\nImages: {len(targets)} targets total, "
        f"{len(targets) - len(targets_with_image)} have no image, "
        f"{already_complete} already complete, "
        f"{len(to_download)} to download"
    )

    if not to_download:
        click.echo("All images already downloaded.")
        return

    completed = 0
    failed = 0

    http_session = requests.Session()
    http_session.headers.update(make_headers(api_key))

    def download_target_image(target: dict) -> tuple[str, bool]:
        tid = target["id"]
        url = target["imageUrl"]

        # Layer 2: check individual file on disk (any extension)
        existing = list(targets_dir.glob(f"{tid}.*"))
        if existing and existing[0].stat().st_size > 0:
            return tid, True

        ext = ext_from_url(url)
        dest = targets_dir / f"{tid}{ext}"
        ok = download_file(url, dest, http_session)
        return tid, ok

    with click.progressbar(length=len(to_download), label="Downloading target images") as bar:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(download_target_image, t): t for t in to_download}
            for future in as_completed(futures):
                tid, ok = future.result()
                if ok:
                    done.add(tid)
                    completed += 1
                else:
                    failed += 1
                # Persist progress every 25 completions
                if (completed + failed) % 25 == 0:
                    save_done_set(progress_file, done)
                bar.update(1)

    save_done_set(progress_file, done)

    click.echo(
        f"\nDone. Downloaded: {completed}, Failed: {failed}, "
        f"Total complete: {len(done)}/{len(targets)}"
    )


# ---------------------------------------------------------------------------
# pull-sessions command
# ---------------------------------------------------------------------------


@cli.command("pull-sessions")
@click.option("--limit", default=None, type=int, help="Max number of sessions to process")
@click.option(
    "--parallel",
    default=DEFAULT_PARALLEL,
    show_default=True,
    type=int,
    help="Concurrent media downloads",
)
@click.pass_context
def pull_sessions(ctx: click.Context, limit: Optional[int], parallel: int) -> None:
    """Download all sessions: media into sessions/<id>/ and metadata into sessions.csv + users.csv."""
    obj = ctx.obj
    api_key: str = obj["api_key"]
    base_url: str = obj["base_url"]
    output_dir: Path = obj["output_dir"]

    sessions_dir = output_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    progress_file = output_dir / ".progress" / "sessions_done.json"
    done = load_done_set(progress_file)

    # --- 1. Fetch all session metadata ---
    sessions, sessions_first_page = fetch_all_pages(
        base_url,
        api_key,
        "/api/research/sessions",
        {
            "sort_key": "submission_time",
            "sort_direction": "asc",
            "include_non_public": "true",
        },
        "sessions",
        limit=limit,
    )

    if not sessions:
        click.echo("No sessions found.")
        return

    write_opt_out_summary(output_dir, sessions_first_page)

    # --- 2. Write sessions.csv ---
    csv_path = output_dir / "sessions.csv"
    write_csv(csv_path, SESSIONS_CSV_FIELDS, [flatten_session(s) for s in sessions])

    # --- 3. Download session media ---
    sessions_with_media = [s for s in sessions if s.get("sessionMediaUrls")]
    sessions_without_media = [s for s in sessions if not s.get("sessionMediaUrls")]

    # Sessions with no media are immediately marked done
    for s in sessions_without_media:
        done.add(s["id"])

    to_download = [s for s in sessions_with_media if s["id"] not in done]

    click.echo(
        f"\nMedia: {len(sessions)} sessions total, "
        f"{len(sessions_without_media)} have no media, "
        f"{len(done) - len(sessions_without_media)} already complete, "
        f"{len(to_download)} to download"
    )

    if to_download:
        completed = 0
        failed_sessions = 0

        http_session = requests.Session()
        http_session.headers.update(make_headers(api_key))

        def download_session_media(session: dict) -> tuple[str, bool]:
            sid = session["id"]
            media_list: list[dict[str, Any]] = session.get("sessionMediaUrls", [])
            session_dir = sessions_dir / sid
            session_dir.mkdir(parents=True, exist_ok=True)

            all_ok = True
            for idx, media in enumerate(media_list):
                url = media.get("url", "")
                mime = media.get("mime_type", "")
                if not url:
                    continue

                ext = ext_from_mime(mime) if mime else ext_from_url(url)
                dest = session_dir / f"{idx}{ext}"

                # Layer 2: skip if file already exists and is non-empty
                if dest.exists() and dest.stat().st_size > 0:
                    continue

                ok = download_file(url, dest, http_session)
                if not ok:
                    all_ok = False

            return sid, all_ok

        with click.progressbar(
            length=len(to_download), label="Downloading session media"
        ) as bar:
            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {
                    executor.submit(download_session_media, s): s for s in to_download
                }
                for future in as_completed(futures):
                    sid, ok = future.result()
                    if ok:
                        done.add(sid)
                        completed += 1
                    else:
                        failed_sessions += 1
                    if (completed + failed_sessions) % 25 == 0:
                        save_done_set(progress_file, done)
                    bar.update(1)

        save_done_set(progress_file, done)

        click.echo(
            f"\nMedia downloads — completed: {completed}, "
            f"had failures: {failed_sessions}"
        )
    else:
        click.echo("All session media already downloaded.")

    # --- 4. Fetch users and write users.csv ---
    click.echo("\nFetching users ...")
    users, _ = fetch_all_pages(
        base_url,
        api_key,
        "/api/research/users",
        {},
        "users",
    )

    users_csv_path = output_dir / "users.csv"
    write_csv(users_csv_path, USERS_CSV_FIELDS, users)

    click.echo(
        f"\nAll done.\n"
        f"  sessions.csv  — {len(sessions)} rows\n"
        f"  users.csv     — {len(users)} rows\n"
        f"  sessions/     — media in {sessions_dir}"
    )


# ---------------------------------------------------------------------------
# pull-users command
# ---------------------------------------------------------------------------


@cli.command("pull-users")
@click.pass_context
def pull_users(ctx: click.Context) -> None:
    """Fetch all users and write users.csv."""
    obj = ctx.obj
    api_key: str = obj["api_key"]
    base_url: str = obj["base_url"]
    output_dir: Path = obj["output_dir"]

    users, users_first_page = fetch_all_pages(
        base_url,
        api_key,
        "/api/research/users",
        {},
        "users",
    )

    write_opt_out_summary(output_dir, users_first_page)

    users_csv_path = output_dir / "users.csv"
    write_csv(users_csv_path, USERS_CSV_FIELDS, users)

    click.echo(f"\nDone. {len(users)} users written to {users_csv_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
