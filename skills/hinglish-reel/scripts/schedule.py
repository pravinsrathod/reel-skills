#!/usr/bin/env python3
"""Scene schedule from the voiceover: the voice is the clock.

Each scene starts `lead` seconds before its line (0.1 s for the first scene, 0.2 s otherwise)
and holds `tail` seconds after the line ends. Writes .tx/sched.json:
{"total": s, "scenes": {id: {"start", "dur", "vo"}}} and prints every caption word at its
scene-local time, which is what scene animations should be keyed to.

reel.json: "scenes": [ids in order], optional "tails": {id: seconds}.
Usage: schedule.py <project>
"""
import json, os, sys

proj = os.path.abspath(sys.argv[1])
cfg = json.load(open(os.path.join(proj, "reel.json")))
words = json.load(open(os.path.join(proj, ".tx/words.json")))
order = cfg["scenes"]
tails = {order[0]: 0.5, order[-1]: 1.8, **cfg.get("tails", {})}
t, out = 0.0, {}
for i, id_ in enumerate(order):
    lead = 0.1 if i == 0 else 0.2
    w = words[id_]
    end = max(w["dur"], w["words"][-1]["end"])
    dur = round(lead + end + tails.get(id_, 0.45), 2)
    out[id_] = {"start": round(t, 3), "dur": dur, "vo": round(t + lead, 3), "lead": lead}
    print(f"{id_:8} start {t:6.2f}  dur {dur:5.2f} | " + " ".join(f"{x['text']}@{lead + x['start']:.2f}" for x in w["words"]))
    t += dur
total = round(t, 2)
json.dump({"total": total, "scenes": out}, open(os.path.join(proj, ".tx/sched.json"), "w"), indent=1)
print(f"total {total}s")
# One frame per scene, late enough that its objects have landed: paste into `npx hyperframes snapshot --at`.
print("snapshot --at " + ",".join(f"{v['start'] + v['dur'] * 0.72:.1f}" for v in out.values()) + " --no-end")
