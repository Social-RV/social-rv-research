# Social RV Research Dataset

This document describes the folder structure and data columns included in the Social RV research export.

This is a full dump of all sessions, targets, and users on the platform. Only users who have opted in to sharing their data with vetted researchers are included (users can toggle this off in their account settings).

For user privacy, email addresses are not included. Each user has a stable UUID that links their sessions to their user record.

## User permission & data completeness

When users sign up on the platform, the Terms & Conditions state that their sessions may be used for research. Users also have a setting on their profile page ("My private sessions can be shared with vetted researchers") which defaults to on. Only users with this setting enabled are included in this dataset.

The export includes an `opt_out_summary.json` file reporting how many users have opted out and how many submitted sessions those users had (all excluded from this dataset). If opting out correlates with performance (e.g. viewers who did poorly and then opted out), the missing data could bias analyses — check the summary to judge whether that matters for your study.

## Session content: media and text

Users upload an arbitrary number and mix of PDFs and images as their session work. Each session's media is stored in its own folder named by session ID. Files are indexed (`0.jpg`, `1.pdf`, `2.png`, etc.) in the order they were uploaded. The `sessions.csv` file contains all metadata; use the session ID to locate the corresponding media folder.

Users can also type their session as plain text directly in the app instead of (or in addition to) uploading files. That text is in the `session_text` column. A session may have media files, typed text, or both — check both when reconstructing a session's content.

## Low-value sessions

Sessions flagged as `is_low_value = true` were identified by an AI that reviews uploaded session media and determines whether the user submitted a genuine set of remote viewing notes or a random/unrelated image to bypass the upload requirement.

## AI judging: decoy judge (v2 + legacy) and TARG judge

Every session is scored by AI judges, and each judge's runs are tracked separately:

**Decoy judge** — a blind judge is shown the session alongside the real target plus 9 decoy targets and ranks them by similarity. `decoy_rank` of 1 means the judge matched the session to the correct target above all decoys; 10 is worst. `decoy_ids` lists the decoy targets used in that run. `decoy_judge_version` tells you which judge produced the score: `decoy_judge_v2` is the current, more accurate judge (nearly all sessions have been re-scored with it); `legacy` marks scores from the original pipeline. For re-scored sessions, `decoy_legacy_rank` preserves the original score so the two judges can be compared. (Older exports had a `comparative_judging_rank` column — it was an alias of `decoy_rank` and has been removed.)

Note: for a period early in the platform's history, decoys were not collected; those sessions have empty `decoy_ids`.

**TARG judge** — an AI judge scores the session against the real target on the 0–7 TARG scale (`targ_score`, 7 is best) and writes a short justification (`targ_analysis`). This uses the same scale as `self_score` and community scores, so they are directly comparable.

## AI scoring coverage

For some time, users unlocked AI scoring after completing 10 sessions, and had to manually trigger scoring on older sessions. Since then, all sessions have been backfilled with the v2 decoy judge and the TARG judge, so coverage should be near-complete; a small number of sessions may still be missing scores where judging failed or was skipped (e.g. no usable media).

---

## Folder structure

```
research_export/
├── targets/
│   ├── <target_id>.jpg     # one image file per target, filename = target ID
│   └── ...
├── sessions/
│   ├── <session_id>/       # one folder per session, folder name = session ID
│   │   ├── 0.jpg           # session media files, indexed in upload order
│   │   ├── 1.pdf
│   │   └── ...
│   └── ...
├── targets.csv             # target metadata (no images)
├── sessions.csv            # session metadata (no images)
├── users.csv               # anonymized user data (no email)
└── opt_out_summary.json    # how many users opted out of research sharing
```

---

## targets.csv

**`id`** — UUID
Unique identifier for the target. Matches the filename in the `targets/` folder and the `target_id` column in `sessions.csv`.

**`coordinate`** — String
Random alphanumeric coordinate assigned to the target (format: XXXX-XXXX). This is what viewers are given — they never see the target image or description until after submitting.

**`description`** — String
Short text description of the target.

**`ai_caption`** — String
A more verbose AI-generated description of the target image.

**`pool_name`** — String
Hidden metadata we use for tracking rough target type. Not used for anything yet

**`target_pool_id`** — UUID
ID of the target pool. The platform has one main pool (the Social RV Core Pool, ~275 targets) which is what the vast majority of sessions are against. Users can also create their own private target pools for self-tasking. This export only includes targets and sessions from the main platform pool, so this value will be the same across all rows.

**`created_at`** — DateTime
When the target was added to the platform (ISO 8601).

---

## sessions.csv

**`id`** — UUID
Unique identifier for the session. Matches the folder name in `sessions/`.

**`user_id`** — UUID
ID of the user who created the session. Links to `id` in `users.csv`.

**`user_display_name`** — String
User's chosen display name on the platform.

**`tasking_time`** — DateTime
When the user received the target coordinate and started their session (ISO 8601).

**`submission_time`** — DateTime
When the user submitted their completed session (ISO 8601). Null if not yet submitted.

**`target_coordinate`** — String
The coordinate that was assigned to the user for this session (format: XXXX-XXXX).

**`tasking_type`** — String
How the session was tasked, e.g. `practice_session_random_coordinate`, `practice_session_shared_coordinate`, `weekly_session`, `group_session`, `arv_session`, `self_tasked_arv_session`, `solana_precognitive_session`.

**`target_id`** — UUID
ID of the actual target. Links to `id` in `targets.csv` and to the filename in `targets/`.

**`target_description`** — String
Text description of the target.

**`weekly_target_id`** — UUID
If this session was part of a weekly community target, the ID of that weekly target. Null otherwise.

**`group_session_id`** — UUID
If this session is part of a group session, the shared group session ID. Group sessions are when multiple viewers attempt the same target simultaneously, with the reveal happening for everyone at once. The tasker typically selects a target pool rather than a specific target, so neither the viewers nor the tasker know the target in advance. Null if this is a solo session.

**`is_unrevealed_group_session`** — Boolean
True if this session belongs to a group session that has not yet been revealed (still in progress).

**`is_public`** — Boolean
Whether the session is publicly visible to other users on the platform.

**`is_low_value`** — Boolean
Whether the session was flagged as low-quality by AI (e.g., the user uploaded a random image instead of genuine session notes).

**`is_highlighted`** — Boolean
Whether the user has selected this as one of up to 5 favorite sessions to feature on their profile.

**`is_blockchain_verified`** — Boolean
Whether the session submission was timestamped and verified on the Solana blockchain prior to the target reveal, providing a tamper-evident record that the session was submitted before the answer was known.

**`self_score`** — Integer
The user's own rating of how well they think their session matched the target (1–7 Targ scale).
7 is best.

**`community_score_avg`** — Float
Average rating given by other users who scored this session (1–7 Targ scale).
7 is best.

**`community_score_count`** — Integer
Number of community ratings this session has received.

**`decoy_rank`** — Integer
Rank assigned by the blind decoy judge, which compared this session against the real target plus 9 decoys (1 = best match, 10 = worst). See `decoy_ids` and `decoy_judge_version`.

**`decoy_judge_version`** — String
Which decoy judge produced `decoy_rank`: `decoy_judge_v2` (the current, more accurate judge) or `legacy` (the original pipeline). Nearly all sessions have been re-scored with v2.

**`decoy_description`** — String
The decoy judge's written reasoning for its ranking.

**`decoy_legacy_rank`** — Integer
For sessions re-scored by the v2 judge, the original legacy judge's rank — useful for comparing the two judges. Empty when the session was never scored by the legacy judge (or when `decoy_rank` itself is the legacy score).

**`targ_score`** — Float
Score from the AI TARG judge on the 0–7 TARG scale (7 = exceptional match, 0 = no correspondence). Same scale as `self_score` and community scores.

**`targ_analysis`** — String
The AI TARG judge's written analysis of the session against the target.

**`session_text`** — String
Plain-text session content the user typed directly in the app, as an alternative (or addition) to uploaded media. Empty for sessions with only uploaded files.

**`decoy_ids`** — String
Comma-separated list of target IDs used as decoys in the decoy judge run that produced `decoy_rank`. Empty if decoys were not recorded for this session (early platform history).

**`num_comments`** — Integer
Number of comments left on this session by the community.

---

## users.csv

**`id`** — UUID
Unique identifier for the user. Matches `user_id` in `sessions.csv`.

**`display_name`** — String
User's chosen display name on the platform.

**`num_sessions`** — Integer
Total number of sessions submitted by this user on Social RV.

**`estimated_start_date`** — Date
User-reported date when they began practicing remote viewing (may predate their Social RV account).

**`estimated_off_platform_sessions`** — Integer
User-reported number of remote viewing sessions completed outside of this platform.
