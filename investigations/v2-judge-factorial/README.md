# V2 judge model-by-decoy factorial experiment

This directory records the public, sanitized protocol for a shadow evaluation.
Session identifiers, target identifiers, decoy manifests, media, prompts, model
reasoning, credentials, and unpublished outcomes must remain in private Modal
storage, LangSmith, or ignored local outputs. This experiment must never write
production scores or change the current production judge run.

## Question

For the same submitted session and true target, how much of the observed rank
change is attributable to:

1. the judge model;
2. the frozen decoy set; or
3. an interaction between model and decoys?

## Frozen design

The experiment is a paired 2×2 factorial:

| Cell | Model | Decoys |
| --- | --- | --- |
| A | GPT-5.2 | March evaluation set |
| B | GPT-5.2 | production rerun set |
| C | GPT-5 Mini | March evaluation set |
| D | GPT-5 Mini | production rerun set |

All four cells are rerun with the same shadow runner. Existing March and
production ranks are context only; they are not substituted for factorial
cells because their preprocessing, code revision, and presentation order
differ.

### Population

- Begin with the exact intersection of sessions that have:
  - the same known true target in both manifests;
  - nine unique March decoys;
  - nine unique production decoys;
  - usable cached session media and all target images.
- Freeze and hash the complete private manifest before the pilot.
- Preserve exclusions and failures rather than replacing missing ranks with
  losses.
- Do not select sessions from observed rank, viewer performance, target
  performance, or prior significance.

### Controlled inputs

- Use one media preprocessing implementation for every cell.
- Use the same session bytes in all four cells.
- Hold the true target at the same deterministic presentation position across
  both decoy conditions for a session.
- Use a deterministic decoy ordering within each condition and reuse it across
  models.
- Record the exact model identifier returned by the gateway, prompt revision,
  candidate order, retries, token usage, and errors.
- Keep model reasoning and media outside Git.

### Outcomes

- Primary: whether the true target ranks in the top five.
- Secondary: top one, top three, exact rank, mean rank, retry count,
  verification failures, malformed outputs, latency, tokens, and cost.
- Primary estimands:
  - model main effect, averaged over both decoy sets;
  - decoy-set main effect, averaged over both models;
  - model×decoy interaction.
- Report paired transitions and effect-size intervals. Include viewer- and
  target-clustered sensitivity analyses, while keeping the session-independent
  analysis requested by the study owner.
- Treat subgroup analyses as exploratory and disclose multiplicity.

### Pilot and stopping

- Use a deterministic, outcome-blind pilot selected by session-ID hash.
- Inspect only execution validity, media reconstruction, schema conformance,
  trace linkage, and cost during the pilot—not aggregate target-rank outcomes.
- If pilot code changes, discard and rerun the pilot cells.
- Project full-cohort cost from measured usage before scaling.
- Stop before projected or observed experiment spend reaches $4,500, leaving a
  reserve below the owner's $5,000 ceiling.
- A provider hard-limit response or unresolved model mismatch stops scaling.

## Storage and provenance

- Existing `eval-data-cache` Modal volume is read-only input.
- A new experiment-specific Modal volume stores the frozen manifest, results,
  checkpoints, and cost ledger.
- New LangSmith projects identify each factorial cell and contain only the
  minimum trace metadata needed for auditing.
- Production Postgres and object storage remain permanently read-only.
- Historical LangSmith results must not be promoted into production or marked
  current.

## Gemini 3.1 Flash Lite extension

After completing the 2×2 experiment, add one pre-specified exploratory cell:

| Cell | Model | Decoys |
| --- | --- | --- |
| E | Gemini 3.1 Flash Lite | March evaluation set |

Cell E reuses the validated factorial manifest, cached media, March candidate
IDs, deterministic candidate order, true-target position, prompts, structured
schemas, verification policy, and primary top-five outcome. Its planned
comparisons are E−A (Gemini versus GPT-5.2) and E−C (Gemini versus GPT-5 Mini)
on the exact shared finished-session sets.

Before scaling:

- validate multimodal image/PDF transport through AI Gateway;
- validate strict ranking and verification schemas;
- confirm the resolved model identifier;
- run the existing outcome-blind pilot and project full-cohort cost;
- stop on persistent schema, image, provider, or rate-limit failures.

This extension is exploratory because it was added after observing A–D. It
must remain separate from the original factorial's confirmatory interpretation.

### Compatibility adaptation

The outcome-blind all-Gemini pilot passed image transport and strict ranking
schemas but failed the verification reliability gate, so it must not be
scaled. A revised cell E2 keeps Gemini 3.1 Flash Lite as the multimodal ranking
model and fixes GPT-5 Mini as the text-only reasoning-consistency verifier.

This separates the capability under test—Gemini target ranking—from an
ancillary schema/reasoning check that previously caused Gemini rate-limit and
retry failures. E2 requires a fresh outcome-blind pilot and is reported
separately from the failed E compatibility pilot.
