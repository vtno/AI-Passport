#!/usr/bin/env bash
# Point Claude Code at our LiteLLM gateway.
# Model is selectable as first arg (or ANTHROPIC_MODEL env var).
# Defaults to grok-4.6-ant (Anthropic Messages → OpenAI + reasoning_effort).
#
# Usage:
#   source assets/claude-code-env.sh                    # uses grok-4.6-ant
#   source assets/claude-code-env.sh qwen3.8-27b-ant    # switch to Qwen
#   ANTHROPIC_MODEL=foo-ant source assets/claude-code-env.sh
set -euo pipefail

: "${LITELLM_BASE_URL:?set LITELLM_BASE_URL, e.g. http://localhost:4000}"
: "${LITELLM_API_KEY:?set LITELLM_API_KEY to the LiteLLM master key}"

MODEL="${1:-${ANTHROPIC_MODEL:-grok-4.6-ant}}"

export ANTHROPIC_BASE_URL="${LITELLM_BASE_URL}"
export ANTHROPIC_AUTH_TOKEN="${LITELLM_API_KEY}"
export ANTHROPIC_MODEL="$MODEL"
export ANTHROPIC_SMALL_FAST_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_FABLE_MODEL="$MODEL"
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="${CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS:-1}"
