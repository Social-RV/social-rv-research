---
name: social-rv-research-api
description: Discover and use the Social RV Research API safely, including sessions, targets, anonymized users, pagination, media downloads, and dataset exports. Use when an agent needs to inspect the live API contract, retrieve Social RV research data, troubleshoot Research API requests, or build tools against the API.
---

# Social RV research API

Use the live OpenAPI document instead of relying on remembered signatures.

## Establish access

1. Check whether `RESEARCH_API_KEY` is set without printing its value.
2. If it is absent, tell the researcher to request access at `research@social-rv.com`.
3. Never ask for a key in chat or place it in a command argument, URL, source file, notebook, log, or committed `.env` file.
4. Send the key only in the `X-API-Key` request header.

## Discover the current contract

Fetch and validate the live OpenAPI 3.1 document:

```bash
uv run python .agents/skills/social-rv-research-api/scripts/fetch_openapi.py \
  --output /tmp/social-rv-research-openapi.json
```

Inspect the relevant path, parameters, response schemas, and documented defaults in that file before writing a request. The default source is:

`https://social-rv.com/api/research/openapi.json`

Use `https://social-rv.com/api/research/swagger-ui` for interactive exploration. Do not commit a fetched schema; the hosted document is authoritative and can change independently of this toolkit.

## Query safely

1. Start with the narrowest endpoint and `page_size=1` to confirm authentication and shape.
2. Add only documented filters.
3. Follow `page`, `total_pages`, and related pagination fields until complete.
4. Preserve `opt_out_summary` in every derived dataset where it is returned.
5. Record retrieval time, base URL, filters, and the OpenAPI `info.version`.
6. Treat `sessionMediaUrls` and target `imageUrl` values as signed, short-lived URLs.
7. Avoid bulk media downloads until the metadata query and intended sample are verified.

For a complete local export, use:

```bash
uv run social-rv-export pull-targets
uv run social-rv-export pull-sessions
uv run social-rv-export pull-users
```

Read `docs/export-cli.md` for operation and `docs/dataset.md` before interpreting exported fields.

## Interpret scores carefully

- `ai_judging.decoy.rank`: target rank among the real target and decoys; lower is better.
- `ai_judging.decoy.judge_version`: identifies the scoring pipeline.
- `ai_judging.decoy_legacy`: preserves an earlier result where available; do not mix it silently with the current result.
- `ai_judging.targ.score`: correspondence score on a 0–7 scale; higher is better.
- `self_score` and community scores come from different raters and are not interchangeable with AI judge outputs.
- Missing scores are not automatically zeroes.

## Protect research data

Keep exports outside Git. Do not expose participant-level data, private-session media, signed URLs, or API responses in public issues and pull requests. Follow the data-use terms associated with the researcher's access.
