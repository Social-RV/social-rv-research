---
name: remote-viewing-research
description: Design and execute reproducible research using Social RV remote viewing data. Use when forming hypotheses, choosing outcomes and null models, preparing an analysis plan, evaluating viewer or judge performance, analyzing repeated sessions, or reporting results from the Social RV Research API.
---

# Remote viewing research

Produce a testable analysis plan before running a confirmatory analysis. Treat the platform data as observational unless the study design supports stronger conclusions.

## Define the question

Write down:

1. The hypothesis and its plausible alternative explanations
2. The unit of analysis: session, viewer, target, judging run, or another unit
3. Primary and secondary outcomes
4. Inclusion and exclusion criteria
5. The statistical test or model
6. The null model and expected result under chance
7. Planned subgroup and sensitivity analyses
8. The stopping rule or fixed data cutoff

Label analyses chosen after seeing outcomes as exploratory.

## Audit the available data

Use the `social-rv-research-api` skill to inspect the live API and retrieve a small metadata sample. Then assess:

- Opt-out counts and possible selection bias
- Missing sessions, media, text, targets, and judge outputs
- Changes in tasking, platform behavior, judge version, and judge model/preset (`ai_judging.*.judge_metadata`) over time
- Repeated observations from the same viewers and targets
- Unequal session counts per viewer
- Low-value and unsubmitted-session filters
- Whether unrevealed or group sessions require separate treatment
- Whether timestamps support the intended temporal ordering

Never convert missing scores to zero without a pre-specified justification.

## Prevent leakage

When training or evaluating a model, choose splits that prevent information from crossing between train and test sets:

- Group by target when target-specific features could be learned.
- Group by viewer when viewer style or identity could be learned.
- Use temporal splits when evaluating future generalization.
- Keep all versions or derivatives of the same session together.
- Do not expose the true target, decoy labels, target descriptions, or judge reasoning to a system intended to operate blind.

Document exactly what each model or judge could see.

## Choose appropriate statistics

- Account for viewer- and target-level clustering with hierarchical models, clustered uncertainty, aggregation, or a justified permutation scheme.
- For decoy rank, define the chance distribution from the actual candidate-set construction rather than assuming a generic continuous outcome.
- For repeated tests, identify one primary outcome and control or clearly disclose multiplicity.
- Report effect sizes and uncertainty intervals, not only thresholded p-values.
- Run sensitivity analyses across reasonable filtering choices and judge versions.
- Do not treat self-scores, community scores, decoy rank, and TARG scores as interchangeable measures.

## Preserve reproducibility

Record:

- Hypothesis and analysis-plan revision
- Retrieval timestamp and API base URL
- OpenAPI version
- Endpoint filters and pagination behavior
- Input file hashes or a manifest
- Code revision, dependency lockfile, random seeds, and runtime parameters
- Every transformation from raw records to analyzed rows

Keep raw data and generated results out of Git unless they have been explicitly cleared for public release.

## Report results

Separate:

1. Data provenance and participant consent boundaries
2. Pre-specified analysis
3. Exploratory findings
4. Missingness and exclusions
5. Effect sizes and uncertainty
6. Robustness and sensitivity checks
7. Limitations and alternative explanations

Use neutral language. A statistical departure from a chosen null model does not by itself establish mechanism, causation, or extrasensory perception.
