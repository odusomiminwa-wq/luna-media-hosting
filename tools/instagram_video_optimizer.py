#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

def need(binary):
    if not shutil.which(binary):
        raise SystemExit(f"Missing dependency: {binary}")

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-5000:])
    return p.stdout

def probe(path):
    return json.loads(run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", str(path)
    ]))

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python3 instagram_video_optimizer.py INPUT.mp4 OUTPUT.mp4")
    need("ffmpeg")
    need("ffprobe")
    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2]).resolve()
    if not src.exists():
        raise SystemExit(f"Input not found: {src}")
    if src == dst:
        raise SystemExit("Input and output must be different files.")
    before = probe(src)
    v = next((s for s in before["streams"] if s.get("codec_type") == "video"), None)
    if not v:
        raise SystemExit("Input has no video stream.")
    vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30"
    cmd = [
        "ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(src),
        "-map","0:v:0","-map","0:a:0?","-vf",vf,
        "-c:v","libx264","-preset","medium","-crf","20",
        "-profile:v","high","-level:v","4.1","-pix_fmt","yuv420p",
        "-g","60","-keyint_min","60","-sc_threshold","0",
        "-c:a","aac","-b:a","128k","-ar","48000","-ac","2",
        "-movflags","+faststart","-map_metadata","-1","-map_chapters","-1",
        "-sn","-dn",str(dst)
    ]
    run(cmd)
    after = probe(dst)
    streams = after.get("streams",[])
    av = next((s for s in streams if s.get("codec_type")=="video"),None)
    aa = next((s for s in streams if s.get("codec_type")=="audio"),None)
    checks = {
        "file_exists":dst.exists(),
        "container":after.get("format",{}).get("format_name",""),
        "video_codec":av.get("codec_name") if av else None,
        "width":av.get("width") if av else None,
        "height":av.get("height") if av else None,
        "pixel_format":av.get("pix_fmt") if av else None,
        "audio_codec":aa.get("codec_name") if aa else None,
        "audio_sample_rate":aa.get("sample_rate") if aa else None,
        "audio_channels":aa.get("channels") if aa else None,
        "duration_seconds":float(after.get("format",{}).get("duration",0)),
        "size_bytes":dst.stat().st_size if dst.exists() else 0
    }
    ok = (checks["file_exists"] and "mp4" in checks["container"] and
          checks["video_codec"]=="h264" and checks["width"]==1080 and
          checks["height"]==1920 and checks["pixel_format"]=="yuv420p" and
          (checks["audio_codec"] in (None,"aac")) and
          (checks["audio_codec"] is None or checks["audio_sample_rate"]=="48000"))
    print(json.dumps({"ok":ok,"input":str(src),"output":str(dst),
                      "before":before.get("format",{}),"after":checks},indent=2))
    if not ok:
        raise SystemExit("Validation failed.")

if __name__=="__main__":
    main()
