---
name: hinglish-reel
description: Make a vertical 9:16 Instagram Reel / YouTube Short in Hinglish (Hindi-English) with a female or male Hindi AI voiceover, word-synced captions, music and motion-graphics scenes, rendered to MP4 with HyperFrames. Built for the "3 problems, main hoon (presenter), solution, free offer, agla episode" explainer format that Indian creators, freelancers and SaaS founders use to pitch an app, a feature or a service to a niche (salon, clinic, kirana, gym, coaching). Use this whenever someone wants a reel, short, or vertical explainer/promo video in Hindi or Hinglish, wants "a video like this reel" for an Indian audience, wants to turn a product feature into a reel series episode, or mentions Hindi voiceover with captions, even if they don't say "Hinglish".
compatibility: Needs the HyperFrames skills (npx skills add heygen-com/hyperframes), Node 18+, ffmpeg, and Python 3.10+ with kokoro-onnx and soundfile for the voice.
---

# Hinglish reel

A 40–60 s vertical reel whose voice is the clock: every scene starts on its line, every object lands on the word that names it, and captions light up word by word. The look is one series style (navy ground with a perspective grid, one accent colour, drawn UI on phones) so episodes read as a set.

The pipeline is mostly scripts. Your judgement goes into three places: the script, the custom scenes, and checking the frames.

```
script.tsv + reel.json ──voice.py──▶ vo-*.wav + .tx/words.json
                       ──schedule.py──▶ .tx/sched.json (+ word times per scene)
                       ──scaffold.py──▶ bg, tabs, hook, intro, next scenes
        you write ─────────────────────▶ problem + solution + cta scenes
                       ──build.py──▶ captions.html + index.html (voice, sfx, music placed)
                       ──finish.py──▶ music bed, render, -14 LUFS
```

Scripts are in this skill's `scripts/` folder; run them with `python3 <skill>/scripts/<name>.py <project>`.

## Before you start

Read the `hyperframes` skill once (it holds the composition rules the scenes follow). If it isn't installed, tell the person to run `npx skills add heygen-com/hyperframes` and restart; this skill depends on it and on its `media-use` companion for music.

Check the voice engine: `python3 -c "import kokoro_onnx"` in some Python 3.10+. The scripts look for it in `$HYPERFRAMES_PYTHON`, then `~/.cache/hyperframes/*/bin/python`, then the current Python. If none has it: `pip install kokoro-onnx soundfile` in a venv and set `HYPERFRAMES_PYTHON` to that venv's python.

## 1. Gather

Ask only what you can't find yourself:

- **Topic and audience**: the niche and the product, service or feature. If it's a real product, read its code, docs or site for real feature names, button labels and message copy. Real words make the reel credible; invented ones get noticed.
- **Presenter**: name, handle, and a photo **file path**. An image pasted into chat is not a file on disk; ask the person to save it and send the path. Without a photo the card shows initials.
- **Voice**: female (`hf_alpha`) or male (`hm_omega`). Match the presenter when the presenter speaks in first person.
- **Reference reel** (optional): if they share one, make a contact sheet (`ffmpeg -i ref.mp4 -vf "fps=8/<dur>,scale=270:-1,tile=4x2" -frames:v 1 sheet.jpg`) and follow its beats and pacing, never its branding or text.
- **CTA**: comment-a-keyword, link in bio, DM, or free trial; and what the next episode is.

## 2. Script

The format, about 9–10 scenes:

| Scene | Job | Example line (Roman) |
| --- | --- | --- |
| hook | name the viewer and promise 3 problems; frame 0 is the thumbnail | Salon owner ho? Aapke salon ki teen badi problems. |
| p1, p2, p3 | one concrete pain each, as a scene they recognise | Pehli: din bhar phone pe booking… |
| intro | "Main hoon <name>", then the solution's name | Main hoon Pranjal, aur iska solution hai… |
| 2–3 solution scenes | the fix, per role or per step, with real screens | Reception ke liye: online booking, live queue… |
| cta | the offer | Poora blueprint free chahiye? Comment mein likho SALON. |
| next | the next episode + follow | Agle episode mein… Follow kar lo. |

Give the intro line some length: "Main hoon <full name>, <role>. Aur iska solution hai, …" runs about 4.5–5 s, which keeps the presenter card on screen for 2 s or more. "Main hoon <name>, aur iska solution…" alone flashes the card for under a second.

Write `script.tsv` (Roman caption text and a Devanagari voice text per scene) and `reel.json`. Both formats, with every key explained, are in `references/reel-json.md`; read it before writing them. Show the person the script (Roman column) in chat before generating voice if they're around; it's the cheapest thing to change.

Claims stay true to the source: if the product's docs don't say "50% faster", the reel doesn't either. Sample numbers in mock screens are labelled "SAMPLE".

## 3. Project and voice

```bash
npx hyperframes init <dir> -e blank --non-interactive --skip-skills
# put script.tsv and reel.json in <dir>
python3 <skill>/scripts/voice.py <dir>
python3 <skill>/scripts/schedule.py <dir>
```

`voice.py` prints, per line, how its timing was found: `whisper` (word for word; best), `whisper-span` (counts differ; spread by length), `pauses` or `span` (the transcript was junk, e.g. a row of `ॐ`; timing from the audio's pauses). Read the `heard:` column: it's the Hindi transcript, and if it doesn't sound like your line, the voice garbled it. Rewrite that line's Devanagari (add commas for pauses, spell English words phonetically) and rerun with `--only <id>`.

`schedule.py` prints every caption word at its scene-local time, plus a ready `snapshot --at …` line with one late frame per scene. Keep that output in view while writing scenes, and rerun it whenever a line changes, because every later scene moves.

## 4. Scenes

```bash
python3 <skill>/scripts/scaffold.py <dir>
```

That writes bg, tabs, hook, intro and next from `reel.json`, copies the sound effects, and crops the photo and logo. Then write one file per remaining scene in `<dir>/compositions/<id>.html`. Read `references/scene-patterns.md` first: it lists the example scenes in `references/examples/` (diary + phone, waiting room, WhatsApp chat, lock-screen alert, dashboard click, phones fan, earnings chart, comment CTA…) and the layout and animation rules that keep the check clean. Copy the closest example, keep its structure, change the objects, copy and times.

## 5. Assemble and check

```bash
python3 <skill>/scripts/build.py <dir>
cd <dir> && npx hyperframes check --json
```

Fix every error. Warnings about small text inside drawn phone UI, or a long notification held less than its reading time, are usually acceptable; overlaps that hide a title are not.

Then look: run the `snapshot --at …` line that `schedule.py` printed (add `-o .tx/snap`) and read the contact sheet. Take the times from the latest schedule; times from an earlier one land in the wrong scenes. Things that slipped past the check in the reference reels: a title that wrapped and was covered by the object below it, a title touching the frame edges, tabs lit too early, a photo with square corners poking out of its circle, a QR that rendered as a broken image, a zoom pushing the scene title under an object. Fix, rebuild, snapshot again.

## 6. Music

With a HeyGen login, `media-use` can fetch a catalogue track; without one it generates locally with MusicGen (slow on CPU: 10–30 min for a 28 s seed, run it in the background while you build scenes). Either way, ask for an upbeat instrumental with no vocals, e.g. "upbeat modern indian pop instrumental, light tabla groove, plucky synth, claps, 110 bpm, no vocals". The person's own track is better than either. Then:

```bash
python3 <skill>/scripts/finish.py <dir> music <track>
python3 <skill>/scripts/build.py <dir>     # picks up assets/bgm/bed.wav
```

## 7. Preview and render

Open the Studio preview (`npx hyperframes preview --background`) so the person can watch and edit; render when they approve, or straight away if they asked for the file:

```bash
python3 <skill>/scripts/finish.py <dir> render <name>
```

It renders `renders/<name>.mp4` (1080×1920, 30 fps), brings the audio to -14 LUFS for Reels/Shorts, and prints the measured level. Extract one frame per scene from the MP4 and look at them before sending.

## Delivering

Say in plain words:
- what's in the reel, scene by scene, in one short list;
- what is placeholder or sample (business names, numbers, the handle if they didn't give one);
- that the audio was measured, not heard;
- that three sounds are CC BY and need the credit line from `assets/sfx/CREDITS.md` in the post caption (or swap them for CC0 sounds).

Changes after delivery: edit `script.tsv` / `reel.json` / scenes, rerun from the step that owns the change (a new line → voice.py onward; a new handle → edit `compositions/intro.html` and render), and render again.
