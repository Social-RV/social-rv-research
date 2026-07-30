# Factorial experiment TODO

## Protocol

- [x] Define the 2×2 model-by-decoy cells.
- [x] Choose top-five as the primary outcome.
- [x] Require paired sessions and controlled presentation order.
- [x] Set a $4,500 experiment stop threshold.
- [x] Freeze and hash the private cohort manifest.

## Runner

- [x] Reconstruct and version the ranking and verification prompts.
- [x] Implement common media preprocessing.
- [x] Validate target and decoy identity before every request.
- [x] Validate structured ranking and verification outputs.
- [x] Record usage, resolved model, retries, latency, and errors.
- [x] Add private unit tests for deterministic ordering and validators.

## Pilot

- [x] Create a separate experiment Modal volume.
- [x] Create four separate LangSmith projects.
- [x] Run an outcome-blind pilot in all cells.
- [x] Verify traces, result persistence, idempotency, and cost accounting.
- [x] Project full-cohort cost before scaling.

## Full run

- [x] Launch each cell with bounded concurrency.
- [x] Checkpoint results and cost after every cell.
- [x] Preserve failures and avoid silent retries outside the recorded policy.
- [x] Confirm observed spend remained below the stop threshold.

## Analysis

- [x] Estimate model and decoy main effects.
- [x] Estimate the model×decoy interaction.
- [x] Report paired transitions and exact-rank agreement.
- [x] Run viewer- and target-clustered sensitivity analyses.
- [x] Audit missingness, malformed outputs, retries, and resolved models.

## Reporting

- [x] Verify private manifest and result hashes.
- [x] Run public repository lint and tests.
- [x] Keep unpublished results and participant data out of Git.
- [x] Produce a private evidence-backed report artifact.

## Visualization

- [x] Reconstruct frozen production score-history cohorts.
- [x] Plot cumulative cohort accuracy against global session chronology.
- [x] Add controlled factorial cells on the same session-order axis.
- [x] Preserve only aggregate graph outputs outside Git.
