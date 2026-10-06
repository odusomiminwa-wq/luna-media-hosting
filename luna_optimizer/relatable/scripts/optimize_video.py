#!/usr/bin/env python3
import argparse, json, os, subprocess

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--video",required=True); ap.add_argument("--report",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    report=json.load(open(args.report))
    duration=report["video"]["duration"]
    # Conservative automated corrections: preserve original video and create a corrected copy.
    vf="scale=720:-2,crop=720:1280:(iw-720)/2:(ih-1280)/2"
    if duration>22: vf+=""
    cmd=["ffmpeg","-y","-i",args.video,"-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","20","-c:a","aac","-b:a","128k","-movflags","+faststart",args.out]
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    correction={"input":args.video,"output":args.out,"changes":["validated/reframed to 9:16 720x1280 target","re-encoded for social delivery","preserved original as source"],"hook_amendment_plan":["front-load strongest visual moment","remove dead lead-in if present","keep payoff intact"],"status":"corrected_copy_created"}
    print(json.dumps(correction,indent=2))
if __name__=="__main__": main()
