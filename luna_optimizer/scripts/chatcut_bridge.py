#!/usr/bin/env python3
import argparse, json, os, re

def extract_section(text, heading):
    m = re.search(rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else ""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--brief", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    with open(args.brief, encoding="utf-8") as f:
        brief = f.read()

    idea = extract_section(brief, "Idea")
    warnings = [x.lstrip("- ").strip() for x in extract_section(brief, "Warnings").splitlines() if x.strip() and x.strip() != "- No historical warnings yet."]
    prompt = extract_section(brief, "Generation prompt")

    plan = {
        "schema_version": "1.0",
        "tool": "chatcut",
        "workflow": "luna-video-edit",
        "status": "ready_for_chatcut_agent",
        "source": {
            "idea": idea,
            "generation_prompt": prompt
        },
        "timeline": [
            {"start": 0.0, "end": 3.5, "action": "hook", "instruction": "Keep the strongest visual action immediately visible; remove dead air."},
            {"start": 3.5, "end": 7.5, "action": "development", "instruction": "Maintain continuous realistic motion and tighten any slow transition."},
            {"start": 7.5, "end": 10.0, "action": "payoff", "instruction": "End on the clearest payoff or comment trigger and preserve a clean loop if possible."}
        ],
        "captions": {
            "enabled": True,
            "style": "short readable creator captions",
            "hook_duration_seconds": 3.5
        },
        "format": {"aspect_ratio": "9:16", "target_duration_seconds": 10},
        "identity_lock": "Preserve Luna's exact established face, freckles, hair identity, body proportions and build.",
        "retention_warnings": warnings,
        "next_step": "Open this manifest in ChatCut/Codex MCP and apply the timeline, caption, pacing and export instructions to the source video."
    }
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    print(json.dumps(plan, indent=2))

if __name__ == "__main__":
    main()
