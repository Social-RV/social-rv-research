#!/usr/bin/env python3
"""Fetch and minimally validate the live Social RV Research API schema."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_URL = "https://social-rv.com/api/research/openapi.json"
TIMEOUT_SECONDS = 30


def fetch_document(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise ValueError("OpenAPI URL must use HTTPS unless it points to localhost")

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "social-rv-research-openapi-fetcher/0.1",
        },
    )
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        payload = response.read()

    document = json.loads(payload)
    if not isinstance(document, dict):
        raise ValueError("OpenAPI response must be a JSON object")
    if not str(document.get("openapi", "")).startswith("3."):
        raise ValueError("Expected an OpenAPI 3.x document")
    if not isinstance(document.get("paths"), dict) or not document["paths"]:
        raise ValueError("OpenAPI document has no paths")
    return document


def write_document(document: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=output.parent,
        prefix=f".{output.name}.",
        delete=False,
    ) as temporary:
        temporary.write(rendered)
        temporary_path = Path(temporary.name)
    temporary_path.replace(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and validate the live Social RV Research API OpenAPI document."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="OpenAPI document URL")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write formatted JSON to this path; omit to write it to stdout",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        document = fetch_document(args.url)
        write_document(document, args.output)
    except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Unable to fetch OpenAPI document: {error}", file=sys.stderr)
        return 1

    info = document.get("info", {})
    destination = str(args.output) if args.output else "stdout"
    print(
        f"Fetched {info.get('title', 'OpenAPI document')} "
        f"v{info.get('version', 'unknown')} with {len(document['paths'])} paths to {destination}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
