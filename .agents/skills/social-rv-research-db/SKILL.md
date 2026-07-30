---
name: social-rv-research-db
description: Optional privileged read-only Postgres access to Social RV via RESEARCH_DATABASE_URL (usually a Supabase read replica). Use when that env var is present and the task needs arbitrary SQL beyond the Research API — inventory queries, joins, storage_path discovery — while still downloading media through the Research API sign endpoints. Never write to Postgres or object storage. Do not use for ordinary Research API work; do not ask researchers for this credential.
---

# Social RV research database (privileged)

## When this applies

Most research uses the Research API only (`RESEARCH_API_KEY`). A small number of provisioned environments also have:

| Name | Value |
| ---- | ----- |
| `RESEARCH_DATABASE_URL` | Postgres URI for a **read-only** Social RV database (prefer Supabase **session pooler** against a **read replica**) |

If `RESEARCH_DATABASE_URL` is unset, stay on the Research API. Never ask the user to paste a database URL into chat.

## Read-only — never write production data

**NEVER write to the Postgres database.** Treat it as permanently read-only, even if a mistaken connection could reach a writable primary.

Also treat **production object storage** and any other Social RV production datastores as read-only. Do not upload, update, or delete objects.

If you need to persist results, caches, intermediates, or experiment artifacts, write them to **Modal**, **LangSmith**, local/export directories ignored by Git, or another non-production store — never back into Social RV Postgres or Storage.

Allowed against the DB: `SELECT` (and other read-only inspection). Forbidden: `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, DDL, migrations, or any write RPC.

## How to use it

1. Confirm the var is set without printing it (`test -n "$RESEARCH_DATABASE_URL"`).
2. Use SQL only for inventory and analysis shapes the API does not expose well (joins, aggregates, listing `rv_session_media.storage_path`, etc.).
3. **Media bytes still go through the Research API.** After you have paths/ids from SQL:
   - `POST /api/research/session-media/sign` or `/target-media/sign` (batches of ≤500, `expires_in` up to 86400)
   - Parallel-download signed URLs; cache on Modal volume when possible
4. Expect the replica to lag the primary by seconds to minutes — fine for research.
5. SQL can see rows the Research API would hide (e.g. opted-out users). Signing still enforces Research API eligibility; ineligible paths return as `missing_*` and must not be force-fetched another way.

## Connection notes

- Prefer **session pooler** for long-lived agent/Modal workers (full Postgres session features).
- Use **transaction pooler** only for many short-lived workers, and disable prepared-statement caches in the client.
- Do not put this URL in the public app Doppler (`social-rv` staging/prod). It belongs only in the privileged research Doppler config.

## Safety

- Never log the connection string, put it in a CLI argv, commit it, or write it into notebooks/issues/PRs.
- Do not use the Supabase **service role** key or Storage S3 keys for research agents.
- Keep derived exports out of Git.
