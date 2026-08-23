# Social RV research export CLI

Downloads research data from the Social RV platform into a structured folder layout
with CSV metadata files and raw media files.

## Requirements

Install the project dependencies from the repository root:

```bash
uv sync
```

## Usage

```bash
# Prefer the environment variable so the key is not saved in shell history
export RESEARCH_API_KEY="your-key"

uv run social-rv-export \
  [--base-url https://social-rv.com] \
  [--output-dir ./research_export] \
  COMMAND [OPTIONS]
```

You can set `RESEARCH_BASE_URL` as an environment variable when working against another authorized environment.

### Commands

#### `pull-targets`

Downloads all target images and writes `targets.csv`.

```bash
uv run social-rv-export pull-targets \
  [--limit N]       # max targets to download (omit for all)
  [--parallel N]    # concurrent downloads (default: 8)
```

#### `pull-sessions`

Downloads all session media files, writes `sessions.csv`, and writes `users.csv`.

```bash
uv run social-rv-export pull-sessions \
  [--limit N]       # max sessions to download (omit for all)
  [--parallel N]    # concurrent downloads (default: 8)
```

#### `pull-users`

Writes anonymized opted-in user metadata and the opt-out summary without downloading sessions or media.

```bash
uv run social-rv-export pull-users
```

## Output layout

```
research_export/
├── targets/
│   ├── <target_id>.jpg     # one file per target, named by ID
│   └── ...
├── sessions/
│   ├── <session_id>/       # one folder per session
│   │   ├── 0.jpg           # indexed media files
│   │   ├── 1.pdf
│   │   └── ...
│   └── ...
├── targets.csv             # all target metadata (no images)
├── sessions.csv            # all session metadata (no images)
├── users.csv               # anonymized user data (no email)
├── opt_out_summary.json    # how many users opted out of research sharing
└── .progress/
    ├── targets_done.json   # resumability tracking
    └── sessions_done.json
```

### targets.csv columns

| Column         | Description                                 |
| -------------- | ------------------------------------------- |
| id             | Target ID (links to filename in `targets/`) |
| coordinate     | Random coordinate assigned to the target    |
| description    | Target description                          |
| pool_name      | Name of the target pool                     |
| target_pool_id | Target pool ID                              |
| created_at     | When the target was created                 |
| ai_caption     | AI-generated caption                        |

### sessions.csv columns

| Column                      | Description                                            |
| --------------------------- | ------------------------------------------------------ |
| id                          | Session ID (links to folder in `sessions/`)            |
| user_id                     | User ID (links to `users.csv`)                         |
| user_display_name           | User's display name                                    |
| tasking_time                | When the user started the session                      |
| submission_time             | When the user submitted                                |
| target_coordinate           | Target coordinate                                      |
| tasking_type                | How the session was tasked (practice, weekly, group…)  |
| weekly_target_id            | Weekly community target ID (if applicable)             |
| group_session_id            | Group session ID (if applicable)                       |
| is_unrevealed_group_session | Whether target was unrevealed at session time          |
| is_public                   | Whether the session is publicly visible                |
| is_low_value                | Whether flagged as low-value by AI                     |
| is_highlighted              | Whether highlighted by admins                          |
| is_blockchain_verified      | Whether verified on Solana blockchain                  |
| self_score                  | User's self-assessment (1–7)                           |
| community_score_avg         | Average community rating                               |
| community_score_count       | Number of community ratings                            |
| decoy_rank                  | Decoy judge rank (1 best, 10 worst)                    |
| decoy_judge_version         | `decoy_judge_v2` (current) or `legacy` (original)      |
| decoy_judge_metadata        | JSON snapshot of the decoy judge config (model, etc.)  |
| decoy_description           | Decoy judge's written reasoning                        |
| decoy_legacy_rank           | Original pre-v2 rank, when re-scored by the v2 judge   |
| decoy_legacy_judge_metadata | JSON snapshot for the legacy decoy run, when present   |
| targ_score                  | AI TARG judge score (0–7, 7 best)                      |
| targ_analysis               | AI TARG judge's written analysis                       |
| targ_judge_metadata         | JSON snapshot of the TARG judge config                 |
| session_text                | Plain text typed in the app instead of/besides uploads |
| num_comments                | Number of comments                                     |
| decoy_ids                   | Decoy target IDs from the decoy judge run (comma-sep)  |
| target_id                   | ID of the target (links to `targets.csv`)              |
| target_description          | Target description at session time                     |

### users.csv columns

| Column                          | Description                                    |
| ------------------------------- | ---------------------------------------------- |
| id                              | User ID (links to `user_id` in `sessions.csv`) |
| display_name                    | User's display name                            |
| num_sessions                    | Number of submitted sessions on platform       |
| estimated_start_date            | When the user started remote viewing           |
| estimated_off_platform_sessions | Estimated sessions done off-platform           |

## Resumability

The CLI is fully resumable. If interrupted, re-run the same command and it will:

1. Re-fetch all metadata (fast — no images) and rewrite the CSVs
2. Skip any images/media that were already fully downloaded
3. Re-attempt any files that were only partially downloaded (empty or missing)

Progress is tracked per-item in `.progress/` and per-file by checking file existence on disk.
