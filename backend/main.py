import base64, json, os, subprocess, tempfile
from pathlib import Path
from typing import Optional
import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

APP_VERSION = "0.1.0"
MAX_BYTES = 80 * 1024 * 1024
ALLOWED = {"video/mp4", "video/quicktime", "video/webm", "application/octet-stream"}
app = FastAPI(title="LUNA Studio API", version=APP_VERSION, description="Secure backend for LUNA short-form video review.")

origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "https://odusomiminwa-wq.github.io").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])

@app.get("/")
def root():
    return {"service":"LUNA Studio API","status":"ok","version":APP_VERSION,"features":["health","video-review"],"ai_configured":bool(os.getenv("OPENAI_API_KEY"))}

@app.get("/health")
def health():
    return {"status":"ok","ai_configured":bool(os.getenv("OPENAI_API_KEY")),"version":APP_VERSION}

def extract_frames(path: str, output_dir: str):
    # Sample five frames across the clip; ffmpeg is supplied by the container image.
    probe = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",path],capture_output=True,text=True,timeout=20)
    if probe.returncode != 0:
        raise HTTPException(400, "Could not read this video. Try an MP4, MOV, or WebM file.")
    try: duration = max(float(probe.stdout.strip()), 0.1)
    except ValueError: duration = 0.1
    times = sorted(set([min(duration*ratio, max(duration-0.05, 0)) for ratio in (0.03,0.22,0.45,0.68,0.9)]))
    frames=[]
    for i,t in enumerate(times):
        dest=os.path.join(output_dir,f"frame{i}.jpg")
        run=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(t),"-i",path,"-frames:v","1","-vf","scale=768:-2","-q:v","5",dest,"-y"],capture_output=True,timeout=25)
        if run.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest)>0:
            frames.append((t,dest))
    if not frames: raise HTTPException(400, "No readable video frames could be extracted.")
    return duration, frames

@app.post("/api/analyze")
async def analyze(video: UploadFile = File(...), platform: str = Form("TikTok"), goal: str = Form("Reach & retention"), context: str = Form(""), hook_notes: str = Form(""), payoff_notes: str = Form(""), caption: str = Form("")):
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(503, "AI review is not configured yet. The host needs the OPENAI_API_KEY secret before analysis can run.")
    if video.content_type and video.content_type not in ALLOWED:
        raise HTTPException(415, "Please upload a video file such as MP4, MOV, or WebM.")
    with tempfile.TemporaryDirectory(prefix="luna-review-") as work:
        src=Path(work)/"clip"
        size=0
        with src.open("wb") as out:
            while True:
                chunk=await video.read(1024*1024)
                if not chunk: break
                size += len(chunk)
                if size > MAX_BYTES: raise HTTPException(413, "Video is over the 80 MB limit. Export a smaller copy and try again.")
                out.write(chunk)
        duration, frames=extract_frames(str(src),work)
        content=[{"type":"input_text","text":(
          "You are LUNA Studio's rigorous short-form content auditor. Review this creator's clip using a practical combination of the original LUNA YouTube-agent workflow concepts: hook scoring, packaging/SEO alignment, retention-aware structure, editing recommendations, Shorts-first pacing, and channel/audience fit. Do not claim to run or invoke external skills; apply the relevant review principles directly. "
          "LUNA brand context: realistic luxury lifestyle, glamour and fashion, relatable emotional truths, mystery and unexpected plot twists. Keep the audience broad and audience-inclusive; do not assume the audience is only women. Visual appeal matters, but it should support a memorable moment, mood, story, or payoff. "
          "Inspect the sampled frames and creator notes. Be candid and specific, never promise virality. The frames are snapshots, so do not claim to know actual movement, exact editing pace, audio quality, or real retention unless supported by supplied data. "
          "Score each dimension from 1 to 10: hook (first-frame/first-moment curiosity), visual_clarity (composition, subject readability, visual quality), story_curiosity (emotional tension, mystery, or reason to keep watching), payoff (whether the ending appears to reward the setup, only if evidenced), caption_alignment (fit between the draft caption and visible content), niche_fit (fit with LUNA's brand and audience), and edit_readiness (how close the clip appears to publish-ready from available evidence). "
          "Calculate overall_score as a weighted creative assessment: hook 25%, visual_clarity 20%, story_curiosity 20%, payoff 15%, caption_alignment 10%, niche_fit 5%, edit_readiness 5%; round to one decimal. Verdict guidance: POST = 8.0-10 and no major evident issue; EDIT = 6.0-7.9 or fixable issues; REWORK = below 6.0 or a fundamental mismatch. Use judgment if evidence is insufficient and say so. "
          "Return ONLY valid JSON with keys: overall_score (number 1-10), verdict (POST, EDIT, or REWORK), summary (string), score_rationale (string), scores (object with hook, visual_clarity, story_curiosity, payoff, caption_alignment, niche_fit, edit_readiness each 1-10), strengths (array of strings), fixes (array of strings), first_3_seconds (string), hook_ideas (array of exactly 3 strings), caption_suggestion (string), seo_keywords (array of strings), hashtags (array of strings), audience_fit (string), limitations (array of strings). "
          "Use creator notes as context, but do not invent events, story beats, or platform metrics absent from the evidence. Make SEO suggestions relevant rather than stuffing keywords. Make hook ideas specific to this clip and platform. "
          f"Platform: {platform}. Goal: {goal}. Duration seconds: {duration:.1f}. Additional creator context: {context[:2000]}. Creator's opening-hook notes: {hook_notes[:1500]}. Payoff notes: {payoff_notes[:1500]}. Draft caption: {caption[:2000]}. "
          "Scores are creative assessments, not measured retention or guaranteed outcomes. State that sampled frames cannot verify motion, audio, or audience retention."
        )}]
        for t,p in frames:
            encoded=base64.b64encode(Path(p).read_bytes()).decode("ascii")
            content.append({"type":"input_text","text":f"Sampled frame at {t:.1f} seconds."})
            content.append({"type":"input_image","image_url":f"data:image/jpeg;base64,{encoded}","detail":"low"})
        payload={"model":os.getenv("OPENAI_MODEL","gpt-4.1-mini"),"input":[{"role":"user","content":content}],"max_output_tokens":1600}
        try:
            response=requests.post("https://api.openai.com/v1/responses",headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},json=payload,timeout=120)
            if response.status_code >= 400:
                raise HTTPException(502, "The AI review provider rejected the request. Check backend configuration and usage limits.")
            data=response.json()
            output="\n".join(item.get("text","") for item in data.get("output",[]) if item.get("type")=="message" for item in item.get("content",[]) if item.get("type")=="output_text")
            if not output: raise HTTPException(502, "The AI provider returned no review text.")
            output=output.strip()
            if output.startswith("```"):
                output=output.split("\n",1)[1].rsplit("```",1)[0].strip()
            try: result=json.loads(output)
            except json.JSONDecodeError: raise HTTPException(502, "The AI provider returned an unreadable review. Please retry.")
            # Enforce consistent scoring server-side rather than relying only on model arithmetic.
            score_fields = ("hook", "visual_clarity", "story_curiosity", "payoff", "caption_alignment", "niche_fit", "edit_readiness")
            scores = result.get("scores")
            if not isinstance(scores, dict):
                raise HTTPException(502, "The AI provider returned a review without valid scores. Please retry.")
            try:
                normalized = {key: max(1, min(10, float(scores[key]))) for key in score_fields}
            except (KeyError, TypeError, ValueError):
                raise HTTPException(502, "The AI provider returned incomplete scores. Please retry.")
            weights = {"hook": 0.25, "visual_clarity": 0.20, "story_curiosity": 0.20, "payoff": 0.15, "caption_alignment": 0.10, "niche_fit": 0.05, "edit_readiness": 0.05}
            result["scores"] = {key: round(value, 1) for key, value in normalized.items()}
            result["overall_score"] = round(sum(normalized[key] * weights[key] for key in score_fields), 1)
            result["verdict"] = "POST" if result["overall_score"] >= 8.0 else ("EDIT" if result["overall_score"] >= 6.0 else "REWORK")
            result["duration_seconds"]=round(duration,1)
            result["sampled_frames"]=len(frames)
            result["review_type"]="AI review of sampled frames; not measured audience retention"
            return result
        except requests.Timeout:
            raise HTTPException(504, "The video review took too long. Try a shorter clip.")
        except requests.RequestException:
            raise HTTPException(502, "Could not reach the AI review provider. Please try again.")
