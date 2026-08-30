import yaml

MAIN = "/app/config.yaml"
ADDON = "/app/grok_addon.yaml"

with open(MAIN) as f:
    main = yaml.safe_load(f) or {}
with open(ADDON) as f:
    addon = yaml.safe_load(f) or {}

existing = {m.get("model_name") for m in main.get("model_list", [])}
for m in addon.get("model_list", []):
    if m.get("model_name") not in existing:
        main.setdefault("model_list", []).append(m)

with open(MAIN, "w") as f:
    yaml.safe_dump(main, f, sort_keys=False, default_flow_style=False)
