# litellm-private

Private LiteLLM gateway isolated from `qwen-3.8-serving` so the open-source Qwenchana repo never leaks Grok/SuperGrok OAuth config or tokens.

Original `qwen-3.8-serving/litellm/` stays clean (`git diff` empty). All Grok config + `xai_oauth` token lives here in `/home/tham/litellm` + Docker volume.

## Files

- `config.template.yaml` — copy of Qwenchana template + 3 Grok models with `use_xai_oauth: true` (`litellm/llms/xai/oauth.py:53` / `litellm/llms/xai/chat/transformation.py:32`)
- `render_config.py` — same renderer as upstream (`qwen-3.8-serving/litellm/render_config.py:1`)
- `.env` / `.env.example` — private env (master key, `XAI_API_KEY` optional, `XAI_OAUTH_*`)
- `docker-compose.grok.yml` — **recommended**: override for Qwenchana stack (same `qwenchana` network/db, port 4000)
- `docker-compose.yml` — standalone `litellm-private:4001` with own db/redis (for testing without touching Qwenchana)
- `.gitignore` — ignores `.env`, `auth.json`, `xai_oauth/`

## Two run modes

### A) Override Qwenchana's litellm in-place (shared DB, port 4000) — recommended

```bash
# Keeps vllm + db + redis from qwen-3.8-serving, only swaps litellm config + adds oauth volume
docker compose -f /home/tham/qwen-3.8-serving/docker-compose.yml \
               -f /home/tham/litellm/docker-compose.grok.yml \
               up -d litellm --force-recreate

# One-time OAuth PKCE login (SuperGrok subscription):
docker exec -it litellm litellm xai-oauth login
# -> prints https://auth.x.ai/... -> sign in with X -> callback http://127.0.0.1:56121/callback
# -> writes /root/.config/litellm/xai_oauth/auth.json into volume `qwenchana_xai_oauth_data`

# Verify merged config:
docker compose -f /home/tham/qwen-3.8-serving/docker-compose.yml \
               -f /home/tham/litellm/docker-compose.grok.yml \
               config | grep -A2 "grok-4.6"

# Test
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{"model":"grok-4.6","messages":[{"role":"user","content":"hi"}]}'

curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{"model":"qwen3.8-27b","messages":[{"role":"user","content":"hi"}]}'

# Isolation check (should be empty):
git -C /home/tham/qwen-3.8-serving diff -- litellm/
```

Token refresh is automatic (`oauth.py:74` `_refresh_tokens` with `threading.Lock`), `expires_at` skew 120s.

### B) Standalone on 4001 (own db, no touch to Qwenchana)

```bash
cd /home/tham/litellm
docker compose up -d
docker compose exec litellm litellm xai-oauth login
curl http://localhost:4001/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{"model":"grok-4.6","messages":[{"role":"user","content":"hi"}]}'
# Shares qwen vLLM via external network `qwenchana_default` -> http://vllm:8000/v1
```

## Model list

- `qwen3.8-27b`, `-low/-mid/-high/-xhigh`, `-ant` (Anthropic passthrough to `qwen38-vllm`)
- `grok-4.6`, `grok-4`, `grok-4-fast` (all `xai/*` + `use_xai_oauth: true`)
- Optional `grok-4.6-key` (uncomment, set `XAI_API_KEY` from `console.x.ai`)

## Notes

- ChatGPT OAuth (`litellm/llms/chatgpt/authenticator.py:1`, `docs.litellm.ai/docs/providers/chatgpt`) is the reference impl; `xai_oauth` mirrors it with `XAI_OAUTH_ISSUER=https://auth.x.ai`, `CLIENT_ID=b1a00492-...`, `scope=... grok-cli:access`.
- SuperGrok has no API key; OAuth token is `Bearer` for `https://api.x.ai/v1` (`litellm/constants.py:XAI_API_BASE`).
- Token stored at `~/.config/litellm/xai_oauth/auth.json` (0600) inside volume, never in repo.

