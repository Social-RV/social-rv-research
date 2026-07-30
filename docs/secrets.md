# Secrets and environment variables

Researchers use their own Social RV, Vercel, LangSmith, and Modal accounts.


Create a Doppler project for this repository, such as `social-rv-research`, and add these standard values:

| Name                 | Value                                           |
| -------------------- | ----------------------------------------------- |
| `RESEARCH_API_KEY`   | Your personal Social RV Research API key        |
| `AI_GATEWAY_API_KEY` | Your Vercel AI Gateway API key                  |
| `LANGSMITH_API_KEY`  | Your LangSmith API key                          |
| `LANGSMITH_TRACING`  | The string `true`                               |
| `MODAL_TOKEN_ID`     | The token ID from your Modal token pair         |
| `MODAL_TOKEN_SECRET` | The token secret from the same Modal token pair |

`LANGSMITH_TRACING` is configuration rather than a credential, but it belongs in the same Doppler configuration so research runs consistently emit traces.

### Optional privileged database access

Only for environments Social RV explicitly provisions (not self-serve for ordinary researchers):

| Name | Value |
| ---- | ----- |
| `RESEARCH_DATABASE_URL` | Postgres URI for a **read-only** Social RV database — preferably the Supabase **session pooler** connection string for a **read replica** |

Use this for arbitrary **read-only** SQL. Never write to Postgres or object storage; persist research outputs to Modal, LangSmith, or local exports instead. Download media through the Research API sign endpoints (`/api/research/session-media/sign`, `/api/research/target-media/sign`), not with Storage or service-role keys. See the `social-rv-research-db` skill.

Do **not** put this URL in the main Social RV app Doppler configs (`social-rv` staging/prod) unless you are intentionally wiring the product to the replica.

## Generate a Social RV Research API key

1. Create or sign in to your account at [social-rv.com](https://social-rv.com).
2. Email [research@social-rv.com](mailto:research@social-rv.com) with a short description of your project and request researcher access.
3. After approval, sign out and back in so your account receives its updated researcher status.
4. Open [Social RV settings](https://social-rv.com/settings).
5. Find **Research API**, choose a descriptive name, and select **Generate API key**.
6. Copy the `srv_pk_...` value immediately. Social RV stores only its hash and cannot display it again.
7. Add it to Doppler as `RESEARCH_API_KEY`.

If a key is exposed, revoke it from the same settings section and generate a replacement.

## Generate a Vercel AI Gateway key

This credential pays for and authenticates model calls made through Vercel AI Gateway.

1. Create or sign in to your own [Vercel account](https://vercel.com/signup).
2. Open the AI Gateway API Keys page from the Vercel dashboard.
3. Select **Create key** and give it a name such as `social-rv-research`.
4. Set a spending budget if appropriate for your research.
5. Copy the key immediately; Vercel cannot display it again.
6. Add it to Doppler as `AI_GATEWAY_API_KEY`.

See [Vercel's API key documentation](https://vercel.com/docs/ai-gateway/authentication-and-byok/api-keys) for the current dashboard and CLI instructions.

## Generate a LangSmith key

LangSmith stores experiment runs, evaluations, and traces.

1. Create or sign in to your own [LangSmith account](https://smith.langchain.com).
2. Open **Settings** → **API Keys**.
3. Select **Create API Key**, give it a descriptive name, and create it.
4. Copy the key immediately; LangSmith displays it only once.
5. Add it to Doppler as `LANGSMITH_API_KEY`.
6. Add `LANGSMITH_TRACING` to Doppler with the string value `true`.

See [LangSmith's API key guide](https://docs.langchain.com/langsmith/create-account-api-key) for current instructions.

Traces can contain prompts, model responses, and research records. Do not trace data that your Social RV access terms or research protocol prohibit sending to LangSmith.

## Generate Modal credentials

Modal authentication uses a pair. Both values are required and there is no third authentication value.

1. Create or sign in to your own [Modal account](https://modal.com).
2. Select or create the workspace that will own your research compute and billing.
3. Open that workspace's token settings.
4. Create a new API token for the workspace.
5. Copy both values from the same token:
   - Add the token ID to Doppler as `MODAL_TOKEN_ID`.
   - Add the token secret to Doppler as `MODAL_TOKEN_SECRET`.

The Modal client reads this pair automatically. You can use `modal token new` for interactive local setup, but Doppler-based and automated runs require the two environment variables above. See [Modal's workspace documentation](https://modal.com/docs/guide/workspaces) and [`modal token` reference](https://modal.com/docs/cli/latest/token).

## Run with Doppler

After adding the standard values:

```bash
doppler run -- uv run social-rv-export pull-sessions
```

Ordinary research access is Research API only. Do not add Supabase service-role keys, Storage S3 keys, or the primary (writable) production database URL. If `RESEARCH_DATABASE_URL` is provisioned, it must point at a read-only replica (or equivalent), not the primary writer.

Never commit `.env` files or put credentials in commands, URLs, notebooks, logs, issues, pull requests, or agent conversations. Rotate any credential immediately if it is exposed.
