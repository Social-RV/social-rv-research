# Investigation TODO

## Access and provenance

- [x] Verify the Research API credential with a one-row request.
- [x] Verify the privileged database is read-only and connected to a replica.
- [x] Verify LangSmith project access.
- [x] Verify Modal access to the evaluation cache volume.
- [x] Verify Vercel AI Gateway access without running inference.
- [ ] Record the relevant LangSmith project, experiment, dataset, and run identifiers.
- [ ] Hash private manifests and record the retrieval cutoff.

## Inventory

- [ ] Inventory the Modal cache layout without downloading media.
- [ ] Identify the offline 10k normal and null run manifests.
- [ ] Identify the smaller model/configuration comparison runs.
- [ ] Identify production v2 judge runs, models, prompts, states, retries, and decoys.
- [ ] Inventory session eligibility fields and run-selection/fallback behavior.

## Comparisons

- [ ] Reconcile offline and production session IDs.
- [ ] Explain sessions unique to either set.
- [ ] Compare true targets and ordered decoy sets on shared sessions.
- [ ] Compare model and prompt/configuration identifiers.
- [ ] Compare failures, retries, parsing, duplicate runs, and selected production results.
- [ ] Produce paired rank and top-k transition summaries.

## Statistics page

- [ ] Determine the row ordering behind the cumulative chart.
- [ ] Determine checkpoint construction and sample sizes.
- [ ] Reproduce the one-tailed p-value implementation independently.
- [ ] Verify whether the first chart prefix equals the offline run prefix.
- [ ] Quantify viewer and target clustering sensitivity.

## Controls and sensitivity

- [ ] Validate null candidate balance and top-k calibration.
- [ ] Assess model/configuration selection and multiplicity.
- [ ] Decide whether an inference rerun is necessary.
- [ ] If necessary, run a small paired factor-isolation sample before scaling.

## Reporting

- [ ] Keep private aggregate findings in the ignored output directory.
- [ ] Add tests for reusable audit/statistical code.
- [ ] Run `uv run ruff check .` and `uv run pytest`.
- [ ] Publish only sanitized methodology and code.
