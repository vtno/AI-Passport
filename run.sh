#!/usr/bin/env bash
# Remote runner for AI Passport — no clone, no install. Temp dir cleaned up after.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/vtno/AI-Passport/main/run.sh | bash -s -- claude
#   curl -fsSL https://raw.githubusercontent.com/vtno/AI-Passport/main/run.sh | bash -s -- claude qwen3.8-27b-ant
set -euo pipefail

RAW="https://raw.githubusercontent.com/vtno/AI-Passport/main"
D=$(mktemp -d)
trap 'rm -rf "$D"' EXIT

mkdir "$D/assets"
curl -fsSL "$RAW/claude" -o "$D/claude"
curl -fsSL "$RAW/assets/claude-code-env.sh" -o "$D/assets/claude-code-env.sh"

# The one-liner passes a "claude" keyword (bash -s -- claude [model]);
# consume it so the launcher sees only the model + claude args.
if [ "${1:-}" = "claude" ]; then
  shift
fi

# Run the launcher with the terminal as stdin so interactive prompts
# (gateway URL, API key) work even though this script was piped via curl.
bash "$D/claude" "$@" < /dev/tty
