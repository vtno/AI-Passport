# AI Passport

Preconfigured LiteLLM gateway for multiple subscription providers
(SuperGrok today, ChatGPT later, …) so any harness (Claude Code, OpenCode, curl)
can reach them through one router.

> Codename "AI Passport" is a pun on the Thai government "TH AI Passport" meme.

## Two run modes

### A) Extend an existing serving stack (e.g. Qwenchana) — recommended

**Additive**: the stack keeps its own `litellm` service definition — its env,
config template and renderer are untouched. The override only appends the
Grok models to the stack's rendered config (via `append_grok.py`), adds the
OAuth token volume + callback port. Grok needs no env vars and no vLLM.
The stack's own `litellm/` stays pristine (`git diff` empty).

```bash
./aipass                       # uses ../Qwenchana/docker-compose.yml by default
./aipass /path/to/stack/docker-compose.yml up   # any other compose stack
```

One-time OAuth PKCE login (SuperGrok subscription):

```bash
docker exec -it litellm litellm xai-oauth login
# -> sign in at https://auth.x.ai/... -> callback http://127.0.0.1:56121/callback
```

Verify (Grok models appear alongside the stack's models):

```bash
curl -s http://localhost:4000/v1/models -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

### B) Standalone base (own db/redis, port 4001)

A working gateway with subscription models only — no serving stack required:

```bash
docker compose up -d
docker compose exec litellm litellm xai-oauth login
```

## Models

- Grok (both modes): `grok-4.6` (effort high), `grok-4.6-low` / `-medium` /
  `-high` / `-xhigh`, `grok-4.6-ant` (Claude Code, Anthropic Messages → OpenAI)
- Mode A: the stack's own models (e.g. Qwenchana's `qwen3.8-27b*`) are served
  unchanged by the stack's config.

## Claude Code

Launcher (first arg selects the model, default `grok-4.6-ant`):

```bash
./claude [model_name] [claude args...]
```

One-liner (no clone needed; `LITELLM_API_KEY` from your `.env`):

```bash
LITELLM_BASE_URL=http://localhost:4000 LITELLM_API_KEY=$LITELLM_API_KEY \
bash -c 'source <(curl -sL https://raw.githubusercontent.com/vtno/AI-Passport/main/assets/claude-code-env.sh grok-4.6-ant) && claude'
```

Or clone and source directly (same as Qwenchana):

```bash
source assets/claude-code-env.sh [model] && claude
```

Requires `LITELLM_BASE_URL` + `LITELLM_API_KEY` in the environment.

## Files

- `config.template.yaml` — standalone gateway config (Grok only, mode B)
- `grok_addon.yaml` — Grok model entries appended by mode A
- `append_grok.py` — merges `grok_addon.yaml` into the stack's rendered config
- `render_config.py` — renders the standalone config + Claude-class aliases
  (target via `CLAUDE_ALIAS_*` env vars; `xai/grok-4.6` in mode B)
- `.env` / `.env.example` — private env (master key; mode B only)
- `docker-compose.grok.yml` — additive extension override (mode A)
- `docker-compose.yml` — standalone base (mode B, port 4001)
- `aipass` — path-free runner for mode A
- `claude` — Claude Code launcher (`./claude [model]`)
- `assets/claude-code-env.sh` — Claude Code env wrapper (sourced by `claude` / one-liner)
- `.gitignore` — ignores `.env`, `auth.json`, `xai_oauth/`

## Notes

- SuperGrok has no API key; the OAuth token is sent as `Bearer` to `https://api.x.ai/v1`.
- Token stored at `/root/.config/litellm/xai_oauth/auth.json` (0600) inside the
  `xai_oauth_data` volume, never in the repo. Refresh is automatic.
- `xai_oauth` mirrors LiteLLM's ChatGPT OAuth implementation
  (`litellm/llms/chatgpt/authenticator.py`, docs.litellm.ai/docs/providers/chatgpt).
