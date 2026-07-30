# Investigation TODO

## Access and provenance

- [x] Verify the Research API credential with a one-row request.
- [x] Verify the privileged database is read-only and connected to a replica.
- [x] Verify LangSmith project access.
- [x] Verify Modal access to the evaluation cache volume.
- [x] Verify Vercel AI Gateway access without running inference.
- [x] Record the relevant LangSmith project, experiment, dataset, and run identifiers privately.
- [x] Hash private manifests and record the retrieval cutoff.

## Inventory

- [x] Inventory the Modal cache layout without downloading media.
- [x] Identify the offline 10k normal and null run manifests.
- [x] Identify the smaller model/configuration comparison runs.
- [x] Inventory production v2 judge runs, model evidence, states, retries, and decoys.
- [x] Record where production prompt/model metadata is not retained with judge rows.
- [x] Inventory session eligibility fields and run-selection/fallback behavior.

## Comparisons

- [x] Reconcile offline and production session IDs.
- [x] Explain sessions unique to either set.
- [x] Compare true targets and ordered decoy sets on shared sessions.
- [x] Compare model and available prompt/configuration identifiers.
- [x] Compare failures, retries, parsing, duplicate runs, and selected production results.
- [x] Produce paired rank and top-k transition summaries.

## Statistics page

- [x] Determine the row ordering behind the cumulative chart.
- [x] Determine checkpoint construction and sample sizes.
- [x] Reproduce the one-tailed p-value implementation independently.
- [x] Verify whether the first chart prefix equals the offline run prefix.
- [x] Quantify viewer and target clustering sensitivity.

## Controls and sensitivity

- [x] Validate null candidate balance and top-k calibration.
- [x] Assess model/configuration selection and multiplicity.
- [x] Decide against a broad inference rerun until existing evidence is reconciled.
- [ ] Optionally run a paired factor-isolation sample after the private judge runner is available.

## Reporting

- [x] Keep private aggregate findings in the ignored output directory.
- [x] Add tests for reusable audit/statistical code.
- [x] Run `uv run ruff check .` and `uv run pytest`.
- [x] Publish only sanitized methodology and code.
