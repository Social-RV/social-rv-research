# Social RV research agent instructions

## Purpose

This repository contains public tools and skills for researchers studying Social RV's remote viewing dataset. It does not contain the dataset or grant access to it.

Researchers must already have a Research API key. If they do not, direct them to [research@social-rv.com](mailto:research@social-rv.com). Never ask a user to paste a key into chat, source code, a notebook, an issue, or a pull request.

## Sources of truth

- API guide: `https://social-rv.com/research-api`
- OpenAPI: `https://social-rv.com/api/research/openapi.json`
- Swagger UI: `https://social-rv.com/api/research/swagger-ui`
- Exported dataset fields: `docs/dataset.md`

The live OpenAPI document is authoritative for request and response signatures. Fetch it with `.agents/skills/social-rv-research-api/scripts/fetch_openapi.py` before implementing API-dependent code. Do not maintain a hand-copied API schema in this repository.

## Repository boundary

This directory is published as a standalone repository. All files inside it must work without files from its parent Social RV monorepo.

- Do not import, symlink, or read files outside this directory.
- Keep public utilities, documentation, tests, and dependencies here.
- Use relative symlinks only when their targets are also inside this directory.
- Never add private application code, credentials, research exports, participant data, or unpublished results.

## Python

- Require Python 3.10 or newer.
- Manage dependencies and run commands with `uv`.
- Add runtime dependencies with `uv add` and development dependencies with `uv add --group dev`.
- Keep reusable code in `src/social_rv_research/`.
- Add or update tests for behavioral changes.
- Run `uv run ruff check .` and `uv run pytest` before committing.

## Research API safety

- Send credentials only in the `X-API-Key` header.
- Read the key from `RESEARCH_API_KEY`; never put it in a URL or log it.
- Begin exploratory calls with a small page size.
- Follow pagination metadata instead of assuming one response is complete.
- Treat media URLs as temporary signed URLs and download them only when needed.
- Preserve the API's opt-out summary with derived datasets.
- Keep raw exports and analysis outputs out of Git.

## Research standards

- State the hypothesis, outcome, unit of analysis, exclusions, and statistical test before inspecting outcome data when feasible.
- Separate exploratory analysis from confirmatory analysis.
- Account for repeated sessions from the same viewer; sessions are not automatically independent observations.
- Report missingness, opt-outs, filtering, judge version, and scoring coverage.
- Prevent target leakage when evaluating models or judges. Split related observations by viewer, target, and time where the hypothesis requires it.
- Use appropriate null models and uncertainty estimates. Do not present descriptive patterns as evidence of causation.
- Preserve scripts, parameters, random seeds, API retrieval time, and a hash or manifest of input data.

Use the `remote-viewing-research` skill for hypothesis and analysis work and the `social-rv-research-api` skill for API access.

## Documentation

- Use sentence casing for headings.
- Prefer precise descriptions over claims about remote viewing efficacy.
- Distinguish platform-generated scores, viewer self-scores, community scores, and independent research outcomes.
- Link to the hosted API documentation instead of duplicating signatures that can become stale.

## Public mirror

The private Social RV monorepo is the source of truth. A GitHub Actions workflow publishes this directory to `Social-RV/social-rv-research`. Do not add workflows or code that pull public-repository changes back automatically.
