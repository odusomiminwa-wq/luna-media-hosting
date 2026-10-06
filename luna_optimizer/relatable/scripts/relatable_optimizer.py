#!/usr/bin/env python3
import argparse, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(path, default):
    try:
        with open(path, encoding="utf-8") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return default

def score(report, weights):
    values = {"hook":report.get("hook"),"retention":report.get("retention"),"relatability":report.get("relatability"),"visual_attention":report.get("visual_attention"),"pacing":report.get("pacing"),"payoff":report.get("payoff"),"commentability":report.get("commentability"),"shareability":report.get("shareability")}
    known = [(k,max(0,min(100,float(v))),weights.get(k,0)) for k,v in values.items() if v is not None]
    total = sum(w for _,_,w in known)
    return round(sum(v*w for _,v,w in known)/total,1) if total else None

def main():
    p=argparse.ArgumentParser(); p.add_argument("--idea",required=True); p.add_argument("--report",default=""); args=p.parse_args()
    cfg=load(os.path.join(ROOT,"config.json"),{}); report=load(args.report,{})
    overall=score(report,cfg.get("signals",{}))
    brief=f"""# Luna Relatable Video Optimizer

## Idea
{args.idea}

## Overall score
{overall if overall is not None else "No report supplied"}

## Strategy
Relatable situation -> curiosity -> unexpected moment -> funny/useful takeaway -> Luna reaction.

## Hook test
A. Start at the problem, not the setup.
B. Start with the reaction, then reveal the cause.
C. Start with a visually unusual action that creates an immediate question.

## Retention rules
- First 1-3 seconds must create a reason to keep watching.
- Remove dead walking/setup time unless it itself is the joke.
- Introduce the core problem before 35% of the runtime.
- Add a visual or emotional change every 2-3 seconds when natural.
- End immediately after the payoff; avoid explanation after the joke.

## Relatability test
The viewer should recognize the situation without needing Luna's backstory.
Use ordinary locations, believable behavior, and one specific human problem.

## Luna identity
Keep the exact established Luna face, freckles, hairstyle, body proportions and build consistent.

## Production prompt
Create a photorealistic 9:16 Luna Reel around the idea above. Make the opening immediately understandable or curiosity-inducing. Use natural smartphone/lifestyle cinematography rather than an advertisement. Keep Luna as the main character while allowing realistic background people and environmental activity. Build toward one unexpected, funny, useful, or emotionally recognizable payoff. Avoid generic AI beauty shots, excessive cinematic polish, supernatural effects, random scene changes, and direct-to-camera influencer posing unless the idea requires it.

## Test matrix
1. Hook A: problem first.
2. Hook B: reaction first.
3. Hook C: curiosity first.
Keep the body of the video as similar as possible so we learn which hook wins.
Track 3-second hold, average watch time, completion, shares, saves, comments, profile visits and followers per 1,000 views.
"""
    out=os.path.join(ROOT,"outputs"); os.makedirs(out,exist_ok=True)
    with open(os.path.join(out,"relatable_video_brief.md"),"w",encoding="utf-8") as f: f.write(brief)
    print(brief)

if __name__=="__main__": main()
