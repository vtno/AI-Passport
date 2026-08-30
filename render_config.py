import os
import re
from pathlib import Path

# Claude model classes routed to the anthropic passthrough backend
# (vLLM's native /v1/messages). Claude Code "auto mode" makes side calls
# for claude-sonnet-* (decisions) and claude-haiku-* (quick tasks); listing
# every known class name keeps them from 400-ing as unknown models. The
# list mirrors every claude-* ID hardcoded in the installed Claude Code
# build (see bin/claude strings) incl. -fast/-v1/snapshot variants.
CLAUDE_ALIAS_MODELS = [
    # opus class
    "claude-opus-5",
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-7-fast",
    "claude-opus-4-6",
    "claude-opus-4-6-20251101",
    "claude-opus-4-6-fast",
    "claude-opus-4-6-v1",
    "claude-opus-4-5",
    "claude-opus-4-5-20251101",
    "claude-opus-4-5-20251101-v1",
    "claude-opus-4-1",
    "claude-opus-4-1-20250805",
    "claude-opus-4-1-20250805-v1",
    "claude-opus-4",
    "claude-opus-4-20250514",
    "claude-opus-4-20250514-v1",
    "claude-opus-4-0",
    "claude-3-opus",
    "claude-3-opus-20240229",
    # sonnet class
    "claude-sonnet-5",
    "claude-sonnet-4-6",
    "claude-sonnet-4-6-20251114",
    "claude-sonnet-4-5",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-5-20250929-v1",
    "claude-sonnet-4-5-v1",
    "claude-sonnet-4",
    "claude-sonnet-4-0",
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-20250514-v1",
    "claude-3-7-sonnet",
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet",
    "claude-3-5-sonnet-20241022",
    "claude-3-sonnet",
    "claude-3-sonnet-20240229",
    # haiku class
    "claude-haiku-4-5",
    "claude-haiku-4-5-20251001",
    "claude-haiku-4-5-20251001-v1",
    "claude-haiku-4",
    "claude-haiku-3-5",
    "claude-haiku-3-5-20241022",
    "claude-3-haiku",
    "claude-3-haiku-20240307",
    # fable class
    "claude-fable-5",
    "claude-fable-5-mythos-5",
]

template = Path("/app/config.template.yaml").read_text()
rendered = re.sub(
    r"\$\{([A-Za-z0-9_]+)\}",
    lambda m: os.environ.get(m.group(1), m.group(0)),
    template,
)

# Claude-class alias target is provider-agnostic: each compose mode sets
# CLAUDE_ALIAS_MODEL (+ optional CLAUDE_ALIAS_USE_OAUTH / CLAUDE_ALIAS_API_BASE /
# CLAUDE_ALIAS_API_KEY). Unset -> no aliases are rendered.
alias_model = os.environ.get("CLAUDE_ALIAS_MODEL", "").strip()
if alias_model:
    extra = []
    if os.environ.get("CLAUDE_ALIAS_USE_OAUTH") == "1":
        extra.append("      use_xai_oauth: true")
    if os.environ.get("CLAUDE_ALIAS_API_BASE"):
        extra.append("      api_base: " + os.environ["CLAUDE_ALIAS_API_BASE"])
    if os.environ.get("CLAUDE_ALIAS_API_KEY"):
        extra.append("      api_key: " + os.environ["CLAUDE_ALIAS_API_KEY"])
    alias_block = "\n".join(
        "  - model_name: " + name + "\n"
        "    litellm_params:\n"
        "      model: " + alias_model + "\n" + "\n".join(extra) + "\n"
        for name in CLAUDE_ALIAS_MODELS
    )
else:
    alias_block = ""
rendered = rendered.replace("CLAUDE_ALIAS_DEPLOYMENTS", alias_block.rstrip("\n"))

Path("/app/config.yaml").write_text(rendered)
