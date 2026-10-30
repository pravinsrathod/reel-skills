# reel.json and script.tsv

Both live at the project root. The scripts read them; nothing else does.

## script.tsv

One line per scene, tab-separated, in scene order:

```
<scene id> <TAB> <Roman Hinglish: the captions> <TAB> <Devanagari: what the voice reads>
```

```
hook	Walk-in customers ki line? Token system ki teen problems.	वॉक-इन कस्टमर्स की लाइन? टोकन सिस्टम की तीन प्रॉब्लम्स।
p1	Pehli: kaagaz ke token kho jaate hain, aur printer ka kharcha alag.	पहली: कागज़ के टोकन खो जाते हैं, और प्रिंटर का खर्चा अलग।
```

- Kokoro's Hindi voices mispronounce Roman Hinglish; they read Devanagari well, including English words written phonetically (व्हाट्सऐप, कस्टमर, टोकन). Write brand names as they are said (प्रो ए आई बॉट).
- Keep the two columns saying the same words in the same order. When the word counts match, every caption word gets its spoken time; when they don't, times are spread by length, which is close but looser.
- Keep each line to about 9–15 words (3.5–6 s at speed 1.1). One idea per scene.
- Write gender-neutral first person ("Main hoon …", not "main banaunga/banaungi") unless you know the presenter's.

## reel.json

```json
{
  "title": "ProAiBot token queue",
  "voice": "hf_alpha",
  "speed": 1.1,
  "accent": "#f59e0b",
  "scenes": ["hook", "p1", "p2", "p3", "intro", "scan", "ping", "staff", "cta", "next"],
  "problems": ["p1", "p2", "p3"],
  "tails": { "cta": 0.7 },
  "hook": {
    "icon": "ticket",
    "line1": "WALK-IN KI", "line1_accent": "LINE?",
    "sub": "TOKEN SYSTEM KI", "sub_word": "Token",
    "stamp": "3 PROBLEMS", "stamp_word": "teen"
  },
  "presenter": {
    "first": "Pranjal", "last": "", "handle": "@0209ai_official", "role": "",
    "photo": "~/Downloads/me.jpg", "photo_crop": "584:584:0:372",
    "name_word": "Pranjal", "clear_word": "solution"
  },
  "reveal": {
    "type": "brand", "logo": "~/proj/logo.png",
    "word": "Pro", "word_accent": "AiBot", "word_at": "ProAiBot",
    "chip": "TOKEN QUEUE", "chip_at": "Token"
  },
  "next": {
    "series": "PROAIBOT FEATURES", "ep": "EP 02",
    "title": "WhatsApp pe", "title_accent": "Appointment Booking",
    "title_word": "WhatsApp", "follow_word": "Follow"
  },
  "sfx": [
    { "sound": "pop", "scene": "p1", "at": 0.95 },
    { "sound": "click-soft", "scene": "staff", "word": "click" }
  ],
  "voice_volume": 1.6,
  "music_volume": 0.16
}
```

| Key | Meaning |
| --- | --- |
| `voice` | Kokoro voice. `hf_alpha` / `hf_beta` female, `hm_omega` / `hm_psi` male (all Hindi). |
| `speed` | 1.1 suits reels; 1.0 for a calmer read. |
| `accent` | One colour for the series: highlighted title words, the active tab, the speaking word in captions, the presenter ring. Green `#3dff8f` and amber `#f59e0b` both read well on the navy ground. |
| `scenes` | Scene ids in order. First is the hook, last is the next-episode card, and `intro` must be one of them. |
| `problems` | Exactly three scene ids, lit one by one on the tabs. Omit for a reel without the problem format. |
| `tails` | Seconds held after a line ends (default 0.45; hook 0.5; last scene 1.8). |
| `hook.icon` | `ticket`, `scissors`, `store`, `phone`, `chat`, `clinic`, `rupee`, or raw SVG path markup on a 24×24 grid. |
| `*_word` keys | A caption word (case and punctuation ignored, prefix match) whose spoken time the animation lands on. If it isn't found the script says so and uses a default. |
| `presenter.photo_crop` | ffmpeg `w:h:x:y` square around the face. Without it, a top-aligned centre square is used, which suits most portraits. |
| `reveal.word` / `word_accent` | Printed back to back, so a two-word name needs a trailing space in `word` (`"Hinglish "` + `"Reel"`); a one-word mark like `"Pro"` + `"AiBot"` needs none. |
| `reveal.type` | `brand` (logo + wordmark + chip) for a product; `text` (`line`, `big`, `big_word`) for an idea ("ISKA SOLUTION? / EK APP"). |
| `sfx` | Extra hits. `at` is scene-local seconds, or `word` lands it on a caption word. Whooshes on cuts and the hook impact are added for you. |
