#!/usr/bin/env python3
import argparse, json, os
from statistics import mean

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(path, default):
    if not path:
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def clamp(value, lo=0, hi=100):
    return max(lo, min(hi, float(value)))

def report_score(report, weights):
    parts = {
        "hook": report.get("hook", {}).get("strength"),
        "pacing": report.get("pacing", {}).get("score"),
        "visual_attention": report.get("visual_attention", {}).get("score"),
        "on_screen_text": report.get("on_screen_text", {}).get("score"),
        "payoff": report.get("payoff", {}).get("score"),
        "shareability": report.get("shareability", {}).get("score"),
        "commentability": report.get("commentability", {}).get("score"),
        "safety": report.get("safety_score")
    }
    known = [(k, clamp(v), weights.get(k, 0)) for k, v in parts.items() if v is not None]
    if not known:
        return None
    total_weight = sum(w for _, _, w in known)
    return round(sum(v * w for _, v, w in known) / total_weight, 1) if total_weight else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", required=True)
    parser.add_argument("--report", default="")
    parser.add_argument("--performance", default="")
    args = parser.parse_args()

    strategy = load_json(os.path.join(ROOT, "config", "luna_strategy.json"), {})
    report = load_json(args.report, {})
    performance = load_json(args.performance, [])
    if isinstance(performance, dict):
        performance = [performance]

    score = report_score(report, strategy.get("signals", {}))
    completion = [float(x.get("completion_rate", 0)) for x in performance if x.get("completion_rate") is not None]
    follows = [float(x.get("followers_gained", 0)) for x in performance]

    avg_completion = round(mean(completion), 1) if completion else None
    avg_follows = round(mean(follows), 2) if follows else None

    # Visual hook formulas only. No spoken lines, no direct address, no CTA.
    # Pick the mechanic that fits the idea; these are structural patterns, not scripts.
    hooks = [
        "Absence, then presence: open on the empty space, she enters a beat later.",
        "A gesture that doesn't resolve: a hand hovering, not taking; a glance at something unseen.",
        "Already in motion: never a static opening frame.",
        "Macro-to-reveal: extreme close-up on a small detail, rack-focus pulls back to her.",
        "The wrong detail: something slightly off her established pattern a returning viewer would notice.",
        "Scale drop: the camera pulls back or up until she becomes small against something vast.",
        "Held stillness: she stops completely and the shot holds longer than expected."
    ]

    warnings = []
    if avg_completion is not None and avg_completion < 20:
        warnings.append("Historical completion is low: make the first 3.5 seconds visually immediate and remove setup.")
    if avg_follows is not None and avg_follows < 1:
        warnings.append("Follower conversion is weak, but do not add a spoken CTA or direct address to fix this: strengthen the visual payoff or recurring motif instead.")
    warnings.extend(str(x) for x in report.get("retention_risks", []))

    prompt = f"""Using the attached Luna reference image as the exact character identity: same face, same freckles, same hair, and same body proportions and build throughout, nothing exaggerated or altered.

IDEA: {args.idea}

CHARACTER RULES: Luna never looks directly at the camera. She never smiles at or for the viewer. No spoken narration or dialogue. She never acknowledges being watched.

TIMELINE:
0-3.5s: Visual hook only, built from one of Luna's hook formulas (absence-then-presence, macro-to-reveal, already-in-motion, unresolved gesture, scale drop, or held stillness). No spoken hook, no text addressed to the viewer.
3.5-7.5s: Continuous realistic movement developing the idea, same composed and unaware tone.
7.5-10s: A visual payoff or an unresolved beat. Never a spoken CTA, never a comment prompt, never a resolved explanation.

STYLE: cinematic, quiet luxury, photorealistic, realistic physics, natural body movement, coherent environment, consistent lighting, no random teleporting, no character morphing, no extra fingers or limbs, no unnecessary scene changes.

FENCING IS PAUSED unless explicitly requested by the idea, and even then it stays folded into the mystery (an empty space she enters to practice alone), never framed as skill-demonstration content.
"""

    out_dir = os.path.join(ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    brief = f"""# Luna Video Production Brief

## Idea
{args.idea}

## Optimizer score
{score if score is not None else "No analysis score supplied"}

## Hook formulas to choose from
{chr(10).join("- " + h for h in hooks)}

## Historical signals
- Average completion rate: {avg_completion if avg_completion is not None else "No data"}
- Average followers gained: {avg_follows if avg_follows is not None else "No data"}

## Warnings
{chr(10).join("- " + w for w in warnings) if warnings else "- No historical warnings yet."}

## Generation prompt
{prompt}

## Test plan
Post one controlled variation at a time. Track views, watch time, completion, shares, saves, profile visits and followers gained. Feed the results back into Luna performance data.
"""
    output_path = os.path.join(out_dir, "luna_video_brief.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(brief)
    print(brief)

if __name__ == "__main__":
    main()
