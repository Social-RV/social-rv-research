# Social RV research

Tools and agent skills for studying the Social RV remote viewing dataset.

This repository helps vetted researchers:

- Query sessions, targets, and anonymized users through the Research API
- Export reproducible datasets, including session media and AI judge results
- Inspect the current API contract from its live OpenAPI document
- Design analyses that account for opt-outs, missing scores, target leakage, and repeated observations

The toolkit is open source. Access to research data is not public and requires a Social RV Research API key.

## Request API access

Email [research@social-rv.com](mailto:research@social-rv.com) with a short description of your research project. Never commit an API key or paste one into an issue, pull request, notebook, or agent conversation.

Once approved, provide the key through your environment:

```bash
export RESEARCH_API_KEY="your-key"
```

## API documentation

- [Research API guide](https://social-rv.com/research-api)
- [Interactive Swagger UI](https://social-rv.com/api/research/swagger-ui)
- [OpenAPI 3.1 document](https://social-rv.com/api/research/openapi.json)

The hosted OpenAPI document is the source of truth. Fetch it before writing or changing an integration:

```bash
uv run python .agents/skills/social-rv-research-api/scripts/fetch_openapi.py \
  --output /tmp/social-rv-research-openapi.json
```

## Install

[Install uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```bash
uv sync
```

Python 3.10 or newer is required.

## Export research data

The export is resumable and writes CSV metadata, media files, and an opt-out summary:

```bash
uv run social-rv-export pull-targets
uv run social-rv-export pull-sessions
uv run social-rv-export pull-users
```

Use `uv run social-rv-export --help` for all options. See the [export guide](docs/export-cli.md) and [dataset reference](docs/dataset.md) for output details.

Downloaded research data is ignored by Git. Store it according to the terms under which access was granted.

## Agent skills

Canonical skills live in `.agents/skills`. Compatibility symlinks expose them to other agent harnesses.

- `social-rv-research-api`: discover and query the live Research API safely
- `remote-viewing-research`: develop hypotheses and reproducible analysis plans for Social RV data

Repository-wide agent instructions are in [AGENTS.md](AGENTS.md).

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run pytest
```

This public repository is generated from the `social-rv-research/` directory in the main Social RV repository. The private monorepo is the source of truth; automated syncs publish only this directory.

## License

A license must be selected before the first public release. Until then, no permission to copy, modify, or redistribute the code is granted.
