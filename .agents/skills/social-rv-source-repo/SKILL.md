---
name: social-rv-source-repo
description: Explains that the private Social RV application monorepo (github.com/Social-RV/social-rv) is the source of truth for the product and Research API implementation. Use when an agent needs application source code, Research API server implementation details, or is deciding whether to clone the main Social RV repo versus working only from this public research toolkit.
---

# Social RV source repository

## What it is

The private application monorepo:

**https://github.com/Social-RV/social-rv**

It contains the Social RV product (Remix app, Research API routes, judges, database migrations, etc.). This public toolkit (`social-rv-research`) is a published slice of that monorepo for researchers.

## When to clone it

If you need to inspect **implementation source** (how the Research API is built, schema migrations, scoring pipelines, product behavior not documented here), you may try cloning or browsing:

```bash
git clone https://github.com/Social-RV/social-rv.git
```

Prefer the hosted Research API docs and live OpenAPI for request/response contracts. Use the private repo only when source-level understanding is actually required.

## If GitHub access fails

Access to `Social-RV/social-rv` is **not** guaranteed. This public research repo is often used by people and agents who only have researcher credentials, not monorepo access.

If clone/fetch/API access fails with auth or permission errors:

1. Treat that as **intentional** — do not retry with alternate credentials, tokens, or workarounds.
2. Do not ask the user to paste a GitHub token or grant access unless they already offered.
3. Continue the task using this toolkit, the Research API, exported data, and any provisioned read-only DB access you already have.

## Boundary

- Do not assume private monorepo files are available in the current workspace.
- Never copy private credentials, participant data, or unpublished results from the monorepo into this public toolkit.
- This directory must keep working standalone without the parent repo.
