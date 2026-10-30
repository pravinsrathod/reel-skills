#!/usr/bin/env python3
"""Write compositions/captions.html and index.html from the schedule, words and reel.json.

Mounts bg, every scene in reel.json "scenes", tabs (if present) and captions; places each
voice line, the music bed (assets/bgm/bed.wav, if present), a whoosh on every cut, an impact
on the hook stamp, and the sound cues listed in reel.json "sfx". Safe to re-run: it only
rewrites captions.html and index.html.

reel.json "sfx": [{"sound": "pop", "scene": "p1", "at": 0.95}] or {"word": "token"} in place
of "at". Sounds: pop, click-soft, whoosh, whoosh-short, impact-bass-1.
Usage: build.py <project>
"""
import html, json, os, re, subprocess, sys

proj = os.path.abspath(sys.argv[1])
cfg = json.load(open(os.path.join(proj, "reel.json")))
words = json.load(open(os.path.join(proj, ".tx/words.json")))
sched = json.load(open(os.path.join(proj, ".tx/sched.json")))
S, TOTAL, order = sched["scenes"], sched["total"], cfg["scenes"]
ACCENT = cfg.get("accent", "#3dff8f")
# Where each sound's audible hit sits in its file (s), how long to keep, and its level.
SFX = {"pop": (0.1, 0.45, 0.45), "click-soft": (0.005, 0.06, 0.9), "whoosh": (0.38, 0.9, 0.35),
       "whoosh-short": (0.135, 0.6, 0.35), "impact-bass-1": (0.125, 0.78, 0.5)}


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def local(scene, cue):
    if "word" in cue:
        want = norm(cue["word"])
        for w in words[scene]["words"]:
            if norm(w["text"]).startswith(want):
                return S[scene]["lead"] + w["start"] + cue.get("shift", 0)
        sys.exit(f"sfx word '{cue['word']}' not found in {scene}")
    return cue["at"]


# ---- captions: groups of up to 3 words, broken at punctuation and at scene changes
caps = []
for id_ in order:
    for w in words[id_]["words"]:
        caps.append({**w, "start": S[id_]["vo"] + w["start"], "end": S[id_]["vo"] + w["end"], "scene": id_})
groups, cur = [], []
for w in caps:
    if cur and cur[-1]["scene"] != w["scene"]:
        groups.append(cur); cur = []
    cur.append(w)
    if len(cur) == 3 or w["text"][-1] in ",.?:;!":
        groups.append(cur); cur = []
if cur:
    groups.append(cur)
items, js = [], []
for i, g in enumerate(groups):
    st = max(g[0]["start"] - 0.05, 0.12)
    nxt = groups[i + 1][0]["start"] - 0.05 if i + 1 < len(groups) else TOTAL
    en = min(g[-1]["end"] + 0.25, nxt)
    spans = " ".join(f'<span id="cap-{i}-{j}" class="cap-w">{html.escape(w["text"])}</span>' for j, w in enumerate(g))
    items.append(f'    <div id="cap-{i}" class="clip cap-g" data-start="{st:.3f}" data-duration="{en - st:.3f}"><div id="cap-{i}-in" class="cap-in">{spans}</div></div>')
    js.append(f'      pop("#cap-{i}-in", {st:.3f});')
    js += [f'      hi("#cap-{i}-{j}", {w["start"]:.3f});' for j, w in enumerate(g)]
open(os.path.join(proj, "compositions/captions.html"), "w").write(f'''<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
    }}
    .cap-g {{
      position: absolute;
      left: 0;
      right: 0;
      top: 1170px;
      text-align: center;
      overflow: visible;
    }}
    .cap-in {{
      display: inline-block;
      padding: 10px 26px 14px;
      border-radius: 18px;
      background: rgba(5, 8, 15, 0.72);
      font-family: "Inter", sans-serif;
      font-weight: 900;
      font-size: 56px;
      line-height: 1.15;
      color: #ffffff;
      white-space: nowrap;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(items)}
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
      const pop = (s, t) => tl.fromTo(s, {{ scale: 0.86, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.12, ease: "back.out(2)" }}, t);
      // The spoken word takes the accent colour as it is said.
      const hi = (s, t) => tl.fromTo(s, {{ color: "#ffffff" }}, {{ color: "{ACCENT}", duration: 0.06, ease: "none" }}, t);
{chr(10).join(js)}
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
''')

# ---- index.html
def host(id_, start, dur, z, kind="graphics"):
    return (f'      <div id="{id_}" data-composition-id="{id_}" data-composition-src="compositions/{id_}.html" data-start="{start}" '
            f'data-duration="{dur}" data-track-index="{z}" data-track-kind="{kind}" data-width="1080" data-height="1920" style="z-index: {z}"></div>')


H = [host("bg", 0, TOTAL, 1)]
H += [host(id_, S[id_]["start"], S[id_]["dur"], 2 + k % 2) for k, id_ in enumerate(order)]
if os.path.exists(os.path.join(proj, "compositions/tabs.html")) and len(cfg.get("problems", [])) == 3:
    after = order[order.index(cfg["problems"][2]) + 1]
    H.append(host("tabs", 0, S[after]["start"], 4))
H.append(host("captions", 0, TOTAL, 5, "captions"))

FX = ('{&quot;version&quot;:1,&quot;nodes&quot;:[{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;n1&quot;,&quot;params&quot;:{&quot;frequency&quot;:80}},'
      '{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;n2&quot;,&quot;params&quot;:{&quot;frequency&quot;:3000,&quot;gain&quot;:2,&quot;q&quot;:1}},'
      '{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;n3&quot;,&quot;params&quot;:{&quot;limit&quot;:-1}}]}')
A = [f'      <audio id="vo-{id_}" class="clip" src="assets/voice/vo-{id_}.wav" data-start="{S[id_]["vo"]}" data-duration="{words[id_]["dur"]}" '
     f'data-track-index="9" data-volume="{cfg.get("voice_volume", 1.6)}" data-audio-group="voiceover" data-fx-chain="{FX}"></audio>' for id_ in order]

cues = []  # (absolute picture time, sound, name)
hook = cfg.get("hook", {})
if hook.get("stamp_word"):
    cues.append((S[order[0]]["start"] + local(order[0], {"word": hook["stamp_word"]}) + 0.03, "impact-bass-1", "impact-hook"))
for k, id_ in enumerate(order[1:]):
    cues.append((S[id_]["start"] + 0.05, "whoosh" if k % 2 == 0 else "whoosh-short", f"whoosh-{id_}"))
for i, c in enumerate(cfg.get("sfx", [])):
    cues.append((S[c["scene"]]["start"] + local(c["scene"], c), c["sound"], f'{c["sound"]}-{c["scene"]}-{i}'))
for k, (t, snd, name) in enumerate(sorted(cues)):
    peak, dur, vol = SFX[snd]
    A.append(f'      <audio id="sfx-{name}" class="clip" src="assets/sfx/{snd}.mp3" data-start="{max(0, t - peak + 0.033):.3f}" '
             f'data-duration="{dur}" data-track-index="{11 + k % 2}" data-volume="{vol}"></audio>')
if os.path.exists(os.path.join(proj, "assets/bgm/bed.wav")):
    A.append(f'      <audio id="bgm" class="clip" src="assets/bgm/bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" '
             f'data-volume="{cfg.get("music_volume", 0.16)}" data-fade-in="0.05" data-fade-out="1.2"></audio>')

open(os.path.join(proj, "index.html"), "w").write(f'''<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        margin: 0;
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        background: #0a1220;
      }}
      #root {{
        width: 100%;
        height: 100%;
      }}
    </style>
  </head>
  <body>
    <!-- {html.escape(cfg.get("title", "Hinglish reel"))}. Generated by hinglish-reel/scripts/build.py: the voice is the clock. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(H)}

      <!-- Voiceover: Kokoro {cfg.get("voice", "hf_alpha")} (Hindi), speed {cfg.get("speed", 1.1)} -->
{chr(10).join(A)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"total {TOTAL}s · {len(groups)} caption groups · {len(A)} audio clips")
missing = [id_ for id_ in order if not os.path.exists(os.path.join(proj, f"compositions/{id_}.html"))]
if missing:
    print("scenes still to write:", ", ".join(f"compositions/{m}.html" for m in missing))
