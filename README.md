# reel-skills

Agent skills for making short-form video.

## hinglish-reel

Turns a topic into a 40–60 s vertical Instagram Reel / YouTube Short in Hinglish: a Hindi AI voiceover (female or male), word-by-word captions, music, sound effects and motion-graphics scenes, rendered to a 1080×1920 MP4.

It follows the explainer format many Indian creators use: **3 problems → "main hoon …" presenter card → the solution, per role → free offer / CTA → "agla episode" teaser**, in one consistent series look so episodes read as a set.

### Install

```bash
npx skills add heygen-com/hyperframes        # prerequisite: HyperFrames + media-use
npx skills add pravinsrathod/reel-skills     # this skill
```

You also need:

- Node 18+ and ffmpeg
- Python 3.10+ with the Kokoro voice: `pip install kokoro-onnx soundfile` (in a venv is fine; point `HYPERFRAMES_PYTHON` at that venv's python)

### Use it

Ask your agent, for example:

> Make a Hinglish reel for gym owners: 3 problems (attendance register, fee renewals missed, no follow-up), then my app as the solution. Female voice, my photo is ~/Pictures/me.jpg, handle @myhandle, CTA "comment GYM".

It writes the script and shows it to you, generates the voice, builds the scenes, checks the frames and renders `renders/<name>.mp4`.

### What's inside

```
skills/hinglish-reel/
├── SKILL.md                    the workflow
├── scripts/
│   ├── voice.py                Kokoro TTS per line → word timings (falls back to pauses when Whisper fails)
│   ├── schedule.py             scene timings from the voice; prints every word's time
│   ├── scaffold.py             fills the series scenes; crops photo and logo
│   ├── build.py                captions + index.html with voice, sfx and music placed
│   └── finish.py               music bed, render, loudness to -14 LUFS
├── templates/compositions/     background, problem tabs, hook, presenter card, next-episode card
├── references/                 reel.json format, scene-writing rules, 11 example scenes
└── assets/sfx/                 5 sound effects (see CREDITS.md)
```

### Credits

Three bundled sound effects are CC BY. When you publish a reel that uses them, add this line to the post: `Sounds: InspectorJ, Brsjak, aropson (freesound.org, CC BY)`. Details in `skills/hinglish-reel/assets/sfx/CREDITS.md`.
