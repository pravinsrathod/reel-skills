#!/usr/bin/env python3
"""Fill the series scenes (bg, tabs, hook, intro, next) from reel.json and the voice timings.

Run after voice.py and schedule.py. Writes compositions/{bg,tabs,hook,intro,next}.html,
copies the sound effects, and crops the presenter photo and logo into assets/img/.
Existing scene files are kept unless --force (they may hold edits made in Studio).

Usage: scaffold.py <project> [--force]
"""
import json, os, re, shutil, subprocess, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
proj = os.path.abspath(sys.argv[1])
force = "--force" in sys.argv
cfg = json.load(open(os.path.join(proj, "reel.json")))
words = json.load(open(os.path.join(proj, ".tx/words.json")))
sched = json.load(open(os.path.join(proj, ".tx/sched.json")))
S = sched["scenes"]
ACCENT = cfg.get("accent", "#3dff8f")

ICONS = {
    "ticket": '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z" /><path d="M13 5v2" /><path d="M13 17v2" /><path d="M13 11v2" />',
    "scissors": '<circle cx="6" cy="18" r="3" /><circle cx="18" cy="18" r="3" /><path d="M8.1 15.9 20 4" /><path d="M15.9 15.9 4 4" />',
    "store": '<path d="M3 9 4.5 4h15L21 9" /><path d="M3 9h18v2a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0Z" /><path d="M5 13v7h14v-7" /><path d="M10 20v-4h4v4" />',
    "phone": '<rect x="6" y="2" width="12" height="20" rx="2" /><path d="M11 18h2" />',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12Z" />',
    "clinic": '<path d="M12 6v6" /><path d="M9 9h6" /><rect x="3" y="3" width="18" height="18" rx="3" />',
    "rupee": '<path d="M6 3h12" /><path d="M6 8h12" /><path d="M6 13l8.5 8" /><path d="M6 13h3a5 5 0 0 0 0-10" />',
}


def darken(hexc, f=0.82):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def at(scene, word, default, shift=0.0):
    """Scene-local time a caption word starts, so an animation lands as the word is said."""
    if word:
        want = norm(word)
        for w in words[scene]["words"]:
            if norm(w["text"]).startswith(want):
                return round(S[scene]["lead"] + w["start"] + shift, 2)
        print(f"  ! '{word}' not found in {scene}; using {default}")
    return round(default + shift, 2)


def fill(name, vals):
    out = os.path.join(proj, "compositions", name)
    if os.path.exists(out) and not force:
        print(f"  kept {name} (exists; --force to rewrite)")
        return
    s = open(os.path.join(SKILL, "templates/compositions", name)).read()
    for k, v in vals.items():
        s = s.replace("{{" + k + "}}", str(v))
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", s)
    if left:
        sys.exit(f"{name}: unfilled {left}")
    open(out, "w").write(s)
    print(f"  wrote {name}")


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


os.makedirs(os.path.join(proj, "compositions"), exist_ok=True)
os.makedirs(os.path.join(proj, "assets/img"), exist_ok=True)
os.makedirs(os.path.join(proj, "assets/sfx"), exist_ok=True)
for f in os.listdir(os.path.join(SKILL, "assets/sfx")):
    shutil.copy(os.path.join(SKILL, "assets/sfx", f), os.path.join(proj, "assets/sfx", f))

fill("bg.html", {"TOTAL": sched["total"]})

# Hook + problem tabs
h = cfg["hook"]
hid = cfg["scenes"][0]
stamp = at(hid, h.get("stamp_word", "teen"), 2.2, -0.25)
icon = h.get("icon", "ticket")
icon_svg = ICONS.get(icon, icon)
fill("hook.html", {
    "DUR": S[hid]["dur"], "ACCENT": ACCENT,
    "ICON_SVG": f'<svg id="hook-icon" viewBox="0 0 24 24" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon_svg}</svg>',
    "LINE1": h["line1"], "LINE1_ACCENT": h.get("line1_accent", ""), "SUB": h.get("sub", ""), "STAMP": h.get("stamp", "3 PROBLEMS"),
    "SUB_AT": at(hid, h.get("sub_word"), 1.2, -0.1), "STAMP_AT": stamp, "SHAKE_AT": round(stamp + 0.28, 2),
    "OUT_AT": round(S[hid]["dur"] - 0.22, 2),
})
probs = cfg.get("problems", [])
if len(probs) == 3:
    intro_start = S[cfg["scenes"][cfg["scenes"].index(probs[2]) + 1]]["start"]
    fill("tabs.html", {
        "ACCENT": ACCENT, "TABS_END": intro_start, "CHIPS_AT": stamp,
        "P1": S[probs[0]]["start"], "P2": S[probs[1]]["start"], "P3": S[probs[2]]["start"],
        "X3_AT": round(intro_start - 0.5, 2),
    })

# Presenter card
p, rv = cfg["presenter"], cfg.get("reveal", {})
iid = "intro"
if p.get("photo"):
    crop = p.get("photo_crop")
    vf = (f"crop={crop}," if crop else "crop='min(iw,ih)':'min(iw,ih)':(iw-min(iw\\,ih))/2:0,") + "scale=600:600:flags=lanczos"
    ff("-i", os.path.expanduser(p["photo"]), "-vf", vf, "-q:v", "2", os.path.join(proj, "assets/img/presenter.jpg"))
    avatar = '<img id="intro-photo" src="assets/img/presenter.jpg" alt="" />'
else:
    initials = "".join(x[0] for x in (p["first"] + " " + p.get("last", "")).split())[:2].upper()
    avatar = initials
name_at = at(iid, p.get("name_word", p["first"]), 0.6, -0.05)
last_at = at(iid, p.get("last_word", p.get("last") or ""), name_at + 0.5, -0.05) if p.get("last") else name_at
clear_at = at(iid, p.get("clear_word", "solution"), 2.2, -0.35)
role = p.get("role", "")
reveal_html, reveal_js = "", ""
if rv.get("type") == "brand":
    if rv.get("logo"):
        # Trim transparent margins so the mark fills its box.
        src = os.path.expanduser(rv["logo"])
        probe = subprocess.run(["ffmpeg", "-i", src, "-vf", "alphaextract,format=gray,cropdetect=limit=24:round=2:skip=0", "-f", "null", "-"],
                               capture_output=True, text=True).stderr
        m = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", probe)
        if m:
            w, hh, x, y = map(int, m[-1]); side = max(w, hh)
            vf = f"crop={side}:{side}:{max(0, x - (side - w) // 2)}:{max(0, y - (side - hh) // 2)},scale=320:320:flags=lanczos"
        else:
            vf = "scale=320:-1"
        ff("-i", src, "-vf", vf, os.path.join(proj, "assets/img/logo.png"))
        reveal_html += '<img id="intro-logo" src="assets/img/logo.png" alt="" />'
        reveal_js += f'      tl.fromTo("#intro-logo", {{ opacity: 0, scale: 0.3, rotation: -20 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.45, ease: "back.out(1.8)" }}, {at(iid, rv.get("word_at"), clear_at + 0.35, -0.15)});\n'
    reveal_html += f'<div id="intro-word">{rv.get("word", "")}<span>{rv.get("word_accent", "")}</span></div>'
    reveal_js += f'      tl.fromTo("#intro-word", {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }}, {at(iid, rv.get("word_at"), clear_at + 0.5)});\n'
    if rv.get("chip"):
        reveal_html += f'<div id="intro-tag">{rv["chip"]}</div>'
        reveal_js += f'      tl.fromTo("#intro-tag", {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: 0.28, ease: "power4.in" }}, {at(iid, rv.get("chip_at"), clear_at + 1.3, -0.18)});\n'
else:
    reveal_html = f'<div id="intro-line">{rv.get("line", "ISKA SOLUTION?")}<span id="intro-big">{rv.get("big", "EK APP")}</span></div>'
    reveal_js = (f'      tl.fromTo("#intro-line", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }}, {round(clear_at + 0.25, 2)});\n'
                 f'      tl.fromTo("#intro-big", {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power4.in" }}, {at(iid, rv.get("big_word"), clear_at + 1.2, -0.18)});\n')
fill("intro.html", {
    "ACCENT": ACCENT, "ACCENT_DARK": darken(ACCENT), "DUR": S[iid]["dur"], "AVATAR": avatar,
    "FIRST": p["first"], "LAST": p.get("last", ""), "HANDLE": p.get("handle", ""), "ROLE": role,
    "ROLE_HTML": f'<div id="intro-chip" data-var-text="role">{role}</div>' if role else "",
    "ROLE_JS": f'      tl.fromTo("#intro-chip", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.2)" }}, {at(iid, p.get("role_word"), last_at + 0.6)});' if role else "",
    "NAME_AT": name_at, "LAST_AT": last_at, "HANDLE_AT": round(last_at + 0.25, 2), "CLEAR_AT": clear_at,
    "REVEAL_HTML": reveal_html, "REVEAL_JS": reveal_js.rstrip("\n"), "OUT_AT": round(S[iid]["dur"] - 0.22, 2),
})

# Next-episode card
n = cfg["next"]
nid = cfg["scenes"][-1]
tap = at(nid, n.get("follow_word", "follow"), 3.4, 0.05)
fill("next.html", {
    "ACCENT": ACCENT, "DUR": S[nid]["dur"], "SERIES": n.get("series", ""), "EP": n.get("ep", "EP 02"),
    "TITLE": n.get("title", ""), "TITLE_ACCENT": n.get("title_accent", ""),
    "HEAD_AT": at(nid, n.get("title_word"), 1.4, -0.1), "BTN_AT": round(tap - 0.5, 2), "TAP_AT": tap, "DONE_AT": round(tap + 0.1, 2),
})
