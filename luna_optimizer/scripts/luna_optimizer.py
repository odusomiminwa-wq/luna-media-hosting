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

def trend_score(trend_report, weights):
    if not trend_report:
        return None
    parts = {
        "proven_format": trend_report.get("proven_format"),
        "narrative_hook": trend_report.get("narrative_hook"),
        "visual_story": trend_report.get("visual_story"),
        "curiosity_gap": trend_report.get("curiosity_gap"),
        "rewatch_trigger": trend_report.get("rewatch_trigger"),
        "share_trigger": trend_report.get("share_trigger"),
        "adaptability": trend_report.get("adaptability"),
        "luna_differentiation": trend_report.get("luna_differentiation")
    }
    known = [(k, clamp(v), weights.get(k, 0)) for k, v in parts.items() if v is not None]
    if not known:
        return None
    total_weight = sum(w for _, _, w in known)
    return round(sum(v * w for _, v, w in known) / total_weight, 1) if total_weight else None

def choose_story_formula(idea, formulas):
    text = idea.lower()
    rules = [
        (["hotel", "suite", "estate", "villa", "club", "lounge", "private"], "unexplained-arrival"),
        (["bag", "ring", "watch", "key", "letter", "jewelry"], "object-with-history"),
        (["tea", "coffee", "dinner", "spa", "dressing", "ritual"], "ritual-as-luxury"),
        (["restricted", "private", "archive", "runway", "yacht", "lounge"], "access-without-explanation"),
        (["strange", "wrong", "odd", "unexpected", "mysterious"], "curiosity-detour"),
        (["heritage", "old", "vintage", "craft", "historic", "archive"], "heritage-clue")
    ]
    for keywords, formula_id in rules:
        if any(k in text for k in keywords):
            return next((f for f in formulas if f["id"] == formula_id), formulas[0] if formulas else None)
    return next((f for f in formulas if f["id"] == "wrong-detail"), formulas[0] if formulas else None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", required=True)
    parser.add_argument("--report", default="")
    parser.add_argument("--performance", default="")
    parser.add_argument("--trend-report", default="")
    args = parser.parse_args()

    strategy = load_json(os.path.join(ROOT, "config", "luna_strategy.json"), {})
    report = load_json(args.report, {})
    performance = load_json(args.performance, [])
    trend_report = load_json(args.trend_report, {})
    if isinstance(performance, dict):
        performance = [performance]

    score = report_score(report, strategy.get("signals", {}))
    tscore = trend_score(trend_report, strategy.get("trend_intelligence", {}).get("trend_scoring", {}))
    completion = [float(x.get("completion_rate", 0)) for x in performance if x.get("completion_rate") is not None]
    follows = [float(x.get("followers_gained", 0)) for x in performance]
    avg_completion = round(mean(completion), 1) if completion else None
    avg_follows = round(mean(follows), 2) if follows else None

    hooks = [
        "Absence, then presence: open on empty space, then Luna enters a beat later.",
        "Unresolved gesture: a hand hovers, reaches, or stops without explanation.",
        "Already in motion: begin mid-action so the viewer has to catch up.",
        "Macro-to-reveal: start on a luxury detail, then reveal Luna and its context.",
        "Wrong detail: introduce one small inconsistency returning viewers can recognize.",
        "Scale drop: pull back until Luna becomes small against a vast luxury environment.",
        "Held stillness: stop the movement and hold one beat longer than expected."
    ]

    formulas = strategy.get("trend_intelligence", {}).get("story_formulas", [])
    formula = choose_story_formula(args.idea, formulas)

    warnings = []
    if avg_completion is not None and avg_completion < 20:
        warnings.append("Historical completion is low: make the first 3.5 seconds visually immediate and remove setup.")
    if avg_follows is not None and avg_follows < 1:
        warnings.append("Follower conversion is weak: strengthen the recurring motif and story payoff rather than adding a CTA.")
    warnings.extend(str(x) for x in report.get("retention_risks", []))

    trend_note = ""
    if trend_report:
        trend_note = f"""
TREND INTELLIGENCE SCORE: {tscore if tscore is not None else "No trend score"}
Use the researched trend only as a structural signal, not as proof that a format will go viral.
"""
    else:
        trend_note = """
TREND INTELLIGENCE: Use the built-in 2026 luxury-storytelling framework: creator-led discovery,
insider/lore detail, craftsmanship/heritage clues, recurring objects, and story-led short-form.
Do not copy a source Reel frame-for-frame.
"""

    formula_text = formula["structure"] if formula else "Use a visual mystery structure with one clue and an unresolved ending."

    prompt = f"""Using the attached Luna reference image as the exact character identity: same face, same freckles, same hair, and same body proportions and build throughout, nothing exaggerated or altered.

IDEA: {args.idea}

LUXURY STORY FORMULA: {formula.get("name") if formula else "Visual mystery"}
FORMULA: {formula_text}

CHARACTER RULES: Luna never looks directly at the camera. She never smiles at or for the viewer. No spoken narration or dialogue. She never acknowledges being watched. No CTA. No explanation.

TIMELINE:
0-3.5s: Start with immediate visual information and one curiosity gap. Use an object, place, gesture, access clue, or unusual detail.
3.5-7.5s: Let the viewer discover a second clue through realistic movement. Do not explain the meaning.
7.5-10s: End at the moment an answer feels close. Use an unresolved visual beat or clean loop.

STYLE: cinematic quiet luxury, photorealistic, restrained wealth, human-feeling movement, natural physics, realistic environments, coherent lighting, no random teleporting, no character morphing, no extra fingers or limbs, no unnecessary scene changes.

LUXURY STORYTELLING DIRECTION: aspirational visuals + human/lore-driven detail + one ownable recurring motif. Make the viewer feel they discovered something rather than being told something.

FENCING IS PAUSED unless explicitly requested by the idea.
"""

    out_dir = os.path.join(ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    brief = f"""# Luna Video Production Brief

## Idea
{args.idea}

## Optimizer score
{score if score is not None else "No analysis score supplied"}

## Luxury storytelling trend score
{tscore if tscore is not None else "No trend-analysis report supplied"}

## Selected story formula
- {formula.get("name") if formula else "Visual mystery"}
- {formula_text}

## Hook formulas
{chr(10).join("- " + h for h in hooks)}

## Historical signals
- Average completion rate: {avg_completion if avg_completion is not None else "No data"}
- Average followers gained: {avg_follows if avg_follows is not None else "No data"}

## Warnings
{chr(10).join("- " + w for w in warnings) if warnings else "- No historical warnings yet."}

## Trend note
{trend_note.strip()}

## Generation prompt
{prompt}

## Test matrix
1. Same scene + three different opening hooks.
2. Same hook + three different luxury story clues.
3. Same story + two ending treatments: unresolved cut vs clean loop.
4. Track views, watch time, completion, shares, saves, profile visits and followers gained.
5. Keep the winner's underlying structure, then create new subjects rather than reposting the same video.
"""
    output_path = os.path.join(ROOT, "outputs", "luna_video_brief.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(brief)
    print(brief)

if __name__ == "__main__":
    main()
