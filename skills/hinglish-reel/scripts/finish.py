#!/usr/bin/env python3
"""Music bed, render, and loudness for a Hinglish reel.

  finish.py <project> music <track.wav|mp3>   loop/trim the track to the reel's length -> assets/bgm/bed.wav
  finish.py <project> render [name]           render renders/<name>.mp4, normalise to -14 LUFS, report levels

Reels and Shorts play around -14 LUFS; renders with a voice at +4 dB land near -12, so the
render step re-encodes only the audio to -14 LUFS / -1.5 dBTP (the picture is copied as is).
"""
import json, os, subprocess, sys

proj = os.path.abspath(sys.argv[1])
cmd = sys.argv[2]


def run(*a, **kw):
    return subprocess.run(list(a), check=True, stdin=subprocess.DEVNULL, **kw)


def loudness(path):
    p = subprocess.run(["npx", "-y", "hyperframes", "audio", path, "--json"], cwd=proj, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    l = json.loads(p.stdout)["items"][0]["loudness"]
    return l["lufsIntegrated"], l["truePeakDb"]


if cmd == "music":
    total = json.load(open(os.path.join(proj, ".tx/sched.json")))["total"]
    track = os.path.abspath(os.path.expanduser(sys.argv[3]))
    os.makedirs(os.path.join(proj, "assets/bgm"), exist_ok=True)
    out = os.path.join(proj, "assets/bgm/bed.wav")
    tdur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", track]))
    loops = int(total // max(tdur - 1.5, 1)) + 1
    # Chain copies with 1.5 s crossfades so the loop seam is not heard, then trim and fade out.
    ins = sum([["-i", track] for _ in range(loops)], [])
    chain, last = [], "[0]"
    for i in range(1, loops):
        chain.append(f"{last}[{i}]acrossfade=d=1.5:c1=tri:c2=tri[x{i}]"); last = f"[x{i}]"
    chain.append(f"{last}atrim=0:{total},afade=t=in:d=0.05,afade=t=out:st={total - 1.5}:d=1.5,aresample=44100,loudnorm=I=-16:TP=-1.5[out]")
    run("ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(chain), "-map", "[out]", "-ac", "2", out)
    print(f"bed.wav {total}s from {loops} x {tdur:.1f}s · LUFS/TP", loudness(out))

elif cmd == "render":
    name = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(proj)
    out = os.path.join(proj, f"renders/{name}.mp4")
    run("npx", "-y", "hyperframes", "render", "-o", out, "--skill", "hyperframes", cwd=proj)
    tmp = out + ".tmp.mp4"
    run("ffmpeg", "-v", "error", "-y", "-i", out, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp)
    os.replace(tmp, out)
    print(f"{out} · LUFS/TP", loudness(out))
else:
    sys.exit(__doc__)
