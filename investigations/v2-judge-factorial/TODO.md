# Factorial experiment TODO

## Protocol

- [x] Define the 2×2 model-by-decoy cells.
- [x] Choose top-five as the primary outcome.
- [x] Require paired sessions and controlled presentation order.
- [x] Set a $4,500 experiment stop threshold.
- [ ] Freeze and hash the private cohort manifest.

## Runner

- [ ] Reconstruct and version the ranking and verification prompts.
- [ ] Implement common media preprocessing.
- [ ] Validate target and decoy identity before every request.
- [ ] Validate structured ranking and verification outputs.
- [ ] Record usage, resolved model, retries, latency, and errors.
- [ ] Add private unit tests for deterministic ordering and validators.

## Pilot

- [ ] Create a separate experiment Modal volume.
- [ ] Create four separate LangSmith projects.
- [ ] Run an outcome-blind pilot in all cells.
- [ ] Verify traces, result persistence, idempotency, and cost accounting.
- [ ] Project full-cohort cost before scaling.

## Full run

- [ ] Launch each cell with bounded concurrency.
- [ ] Checkpoint results and cost after every cell.
- [ ] Preserve failures and avoid silent retries outside the recorded policy.
- [ ] Stop safely if projected or observed spend reaches the threshold.

## Analysis

- [ ] Estimate model and decoy main effects.
- [ ] Estimate the model×decoy interaction.
- [ ] Report paired transitions and exact-rank agreement.
- [ ] Run viewer- and target-clustered sensitivity analyses.
- [ ] Audit missingness, malformed outputs, retries, and resolved models.

## Reporting

- [ ] Verify private manifest and result hashes.
- [ ] Run public repository lint and tests.
- [ ] Keep unpublished results and participant data out of Git.
- [ ] Produce a private evidence-backed report artifact.
