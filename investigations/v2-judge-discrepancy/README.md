# V2 judge statistics discrepancy

This directory contains the public, sanitized methodology for auditing differences between
offline and production evaluations of the Social RV v2 decoy judge. Participant-level data,
media, signed URLs, trace payloads, private database details, and unpublished numerical results
must remain under an ignored output directory and must not be committed.

## Research question

Why can an offline evaluation and the production statistics page disagree when both appear to
cover roughly the same number of sessions?

The investigation distinguishes five non-exclusive explanations:

1. The compared session sets or their ordering differ.
2. Eligibility filters, missing outputs, or fallback-selection rules differ.
3. Candidate sets differ because decoys were sampled again.
4. Judge model, prompt, inference settings, retry, or parsing behavior differs.
5. The statistics page groups, orders, or computes cumulative results differently from the
   offline evaluator.

Ordinary sampling variability and model-selection effects are retained as alternatives. A
cumulative p-value is not expected to decrease monotonically as observations accumulate.

## Frozen analysis plan

This plan is recorded before inspecting outcome-level records.

### Units and outcomes

- Primary unit: one completed judge run for one eligible session.
- Paired unit: the same session evaluated under two pipelines.
- Primary outcome: whether the true target ranks in the top five.
- Secondary outcomes: top one, top three, exact rank, mean rank, missingness, retries, and errors.
- Chance expectations: derive from the actual candidate-set size; for ten candidates, top-one,
  top-three, and top-five expectations are 10%, 30%, and 50%.

### Inclusion and exclusions

- Begin with the exact session identifiers in each named offline and production run.
- Retain only submitted sessions with usable session content and a known true target for the
  primary comparison.
- Report, rather than silently discard, opted-out users, low-value sessions, unavailable media,
  unrevealed sessions, failed/skipped runs, missing ranks, duplicate runs, and fallback runs.
- Do not replace a missing rank with zero or a loss.
- Analyze repeated viewers and targets with clustered or permutation-based uncertainty in
  sensitivity checks; sessions are not automatically independent.

### Comparisons

1. Reconstruct each run manifest: session ID, true target ID, ordered decoy IDs, model, prompt or
   judge version, timestamps, attempt count, terminal state, and rank.
2. Measure exact session-set overlap and explain every left-only and right-only session by filter
   or missingness category.
3. Determine the ordering used by every cumulative curve. Compare prefixes only after confirming
   that they contain the same session IDs.
4. On shared sessions, compare outcomes in this order:
   - same model and same decoys;
   - same model and different decoys;
   - different model and same decoys;
   - different model and different decoys.
5. Use paired rank changes and paired top-k transitions for shared sessions. Use unpaired
   proportion tests only for genuinely disjoint sets.
6. Recompute the displayed cumulative statistic independently from production rows, including
   the exact tail, continuity, and checkpoint rules.
7. Validate the null run and inspect candidate-size and position balance.

### Statistical interpretation

- Report effect sizes and confidence intervals alongside p-values.
- Treat top five as the primary endpoint; label top one and top three as secondary.
- Disclose that model/configuration selection after smaller evaluations can create winner's
  curse and multiple-testing effects.
- Treat the time-series p-value plot as descriptive unless a sequential testing procedure was
  specified. Crossing or moving away from 0.05 is not independently significant.

### Paid rerun rule

Do not start a broad inference rerun until manifests, filters, ordering, candidate sets, and
existing traces have been reconciled. If inference is still needed, use the smallest paired,
stratified sample that isolates one factor at a time, cache inputs outside Git, set an explicit
cost cap, and record model identifiers and random seeds where supported.

### Fixed cutoff

The observational audit uses run records available at the first successful inventory retrieval.
Any later rerun is a separately labeled sensitivity analysis rather than an extension of the
original evaluation.

## Reproducibility

Record retrieval time, live OpenAPI version, code revision, run identifiers, filters, hashes of
private manifests, random seeds, and every transformation. Commit only code and sanitized
documentation; keep generated manifests and results in `outputs/v2-judge-discrepancy/`.
