#!/usr/bin/env python3
import argparse, json, os, subprocess, math

def run(cmd):
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()

def ffprobe(path):
    data=json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",path]))
    v=next((s for s in data["streams"] if s.get("codec_type")=="video"),{})
    a=next((s for s in data["streams"] if s.get("codec_type")=="audio"),{})
    return {
      "duration":float(data["format"].get("duration",0)),
      "width":int(v.get("width",0) or 0),"height":int(v.get("height",0) or 0),
      "fps":v.get("r_frame_rate","0/1"),"video_codec":v.get("codec_name"),
      "audio":bool(a),"audio_codec":a.get("codec_name"),"size_bytes":os.path.getsize(path)
    }

def scene_score(path):
    try:
        import cv2
        cap=cv2.VideoCapture(path); n=max(1,int(cap.get(cv2.CAP_PROP_FRAME_COUNT))); step=max(1,n//30)
        prev=None; diffs=[]
        i=0
        while True:
            ok,frame=cap.read()
            if not ok: break
            if i%step==0:
                g=cv2.resize(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(160,90))
                if prev is not None: diffs.append(float(cv2.absdiff(g,prev).mean()))
                prev=g
            i+=1
        cap.release()
        if not diffs:return {"motion_score":0,"motion_variance":0}
        return {"motion_score":round(sum(diffs)/len(diffs),2),"motion_variance":round(float(__import__("statistics").pstdev(diffs)),2)}
    except Exception as e:
        return {"motion_score":None,"motion_variance":None,"error":str(e)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--video",required=True); ap.add_argument("--out",required=True); args=ap.parse_args()
    meta=ffprobe(args.video); motion=scene_score(args.video)
    d=meta["duration"]
    report={"video":meta,"visual":motion,"optimization":{}}
    report["optimization"]["format_ok"]=(meta["width"]/max(meta["height"],1) < 0.8)
    report["optimization"]["hook_window_seconds"]=min(3.5,d)
    report["optimization"]["dead_time_risk"]="high" if motion.get("motion_score",0) is not None and motion.get("motion_score",0)<3 else "normal"
    report["optimization"]["recommendations"]=[
      "Make the first 1-3 seconds immediately understandable or curiosity-inducing.",
      "Remove unnecessary lead-in before the first meaningful action.",
      "Preserve the strongest payoff and end immediately after it.",
      "Normalize loudness and keep dialogue/voice-over above music and meme audio.",
      "Keep 9:16 vertical framing and Luna identity continuity."
    ]
    with open(args.out,"w") as f: json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
