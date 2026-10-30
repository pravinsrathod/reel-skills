#!/usr/bin/env python3
"""Voiceover for a Hinglish reel: Kokoro TTS per line, then word timings for the captions.

Reads <project>/script.tsv (id <TAB> Roman Hinglish caption text <TAB> Devanagari TTS text)
and <project>/reel.json ("voice", "speed"). Writes assets/voice/vo-<id>.wav and
.tx/words.json: {id: {"dur": seconds, "words": [{"text", "start", "end"}], "source"}} where
"text" is the Roman caption word and times are seconds into that line's wav.

Usage: voice.py <project> [--only id,id] [--skip-tts]
"""
import argparse, glob, json, os, re, subprocess, sys

DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def find_kokoro_python():
    if os.environ.get("HYPERFRAMES_PYTHON"):
        return os.environ["HYPERFRAMES_PYTHON"]
    cands = glob.glob(os.path.expanduser("~/.cache/hyperframes/*/bin/python")) + [sys.executable, "python3"]
    for py in cands:
        try:
            subprocess.run([py, "-c", "import kokoro_onnx, soundfile"], check=True, capture_output=True)
            return py
        except Exception:
            continue
    sys.exit("kokoro-onnx not found. Install it (pip install kokoro-onnx soundfile) in a Python 3.10+ env "
             "and set HYPERFRAMES_PYTHON to that python.")


def media_dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out.decode().strip())


def transcribe(wav):
    """Whisper (small, Hindi). The CLI prints one JSON 'words' line per segment on stderr."""
    p = subprocess.run(["npx", "-y", "hyperframes", "transcribe", wav, "--model", "small", "--language", "hi", "--json"],
                       stdin=subprocess.DEVNULL, capture_output=True, text=True)
    words = []
    for line in (p.stdout + "\n" + p.stderr).splitlines():
        if '"type":"words"' in line:
            words += json.loads(line)["words"]
    return words


def speech_segments(wav, dur):
    """Spans of speech between pauses >= 0.15 s, for when the transcript is unusable."""
    p = subprocess.run(["ffmpeg", "-v", "info", "-i", wav, "-af", "silencedetect=noise=-35dB:d=0.15", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    segs, t = [], 0.0
    for s, e in zip(starts, ends + [dur]):
        if s - t > 0.1:
            segs.append((t, s))
        t = e
    if dur - t > 0.1:
        segs.append((t, dur))
    return segs or [(0.0, dur)]


def spread(words, a, b):
    """Spread words across [a, b] by character length (a fair proxy for spoken length)."""
    total = sum(len(w) for w in words) or 1
    out, t = [], a
    for w in words:
        d = (b - a) * len(w) / total
        out.append({"text": w, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return out


def align(roman, heard, wav, dur):
    good = [w for w in heard if DEVANAGARI.search(w["text"])]
    usable = heard and len(good) >= 0.6 * len(heard)
    if usable and len(heard) == len(roman):
        return [{"text": r, "start": h["start"], "end": h["end"]} for r, h in zip(roman, heard)], "whisper"
    if usable:
        return spread(roman, heard[0]["start"], heard[-1]["end"]), "whisper-span"
    # Junk transcript (e.g. repeated symbols): split the caption at punctuation and match the
    # pieces to the pauses in the audio when the counts agree.
    segs = speech_segments(wav, dur)
    phrases, cur = [], []
    for w in roman:
        cur.append(w)
        if w[-1] in ",.?:;!":
            phrases.append(cur); cur = []
    if cur:
        phrases.append(cur)
    if len(phrases) == len(segs):
        out = []
        for ph, (a, b) in zip(phrases, segs):
            out += spread(ph, a, b)
        return out, "pauses"
    return spread(roman, segs[0][0], segs[-1][1]), "span"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-tts", action="store_true")
    a = ap.parse_args()
    proj = os.path.abspath(a.project)
    cfg = json.load(open(os.path.join(proj, "reel.json")))
    voice, speed = cfg.get("voice", "hf_alpha"), str(cfg.get("speed", 1.1))
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(proj, "script.tsv"), encoding="utf-8") if l.strip()]
    only = set(filter(None, a.only.split(",")))
    os.makedirs(os.path.join(proj, "assets/voice"), exist_ok=True)
    os.makedirs(os.path.join(proj, ".tx"), exist_ok=True)
    wpath = os.path.join(proj, ".tx/words.json")
    words = json.load(open(wpath)) if os.path.exists(wpath) else {}
    env = dict(os.environ, HYPERFRAMES_PYTHON=find_kokoro_python()) if not a.skip_tts else os.environ
    for id_, roman, dev in rows:
        if only and id_ not in only:
            continue
        wav = os.path.join(proj, f"assets/voice/vo-{id_}.wav")
        if not a.skip_tts:
            subprocess.run(["npx", "-y", "hyperframes", "tts", dev, "-v", voice, "-l", "hi", "-s", speed, "-o", wav, "--json"],
                           stdin=subprocess.DEVNULL, capture_output=True, check=True, env=env, cwd=proj)
        dur = media_dur(wav)
        heard = transcribe(wav)
        aligned, src = align(roman.split(), heard, wav, dur)
        words[id_] = {"dur": round(dur, 3), "words": aligned, "source": src}
        print(f"{id_:8} {dur:5.2f}s  {src:12}  heard: {' '.join(w['text'] for w in heard)[:70]}")
    stray = os.path.join(proj, "assets/voice/transcript.json")
    if os.path.exists(stray):
        os.remove(stray)
    json.dump(words, open(wpath, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
