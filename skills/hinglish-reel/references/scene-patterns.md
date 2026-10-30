# Writing the custom scenes

The scaffold writes the series scenes (bg, tabs, hook, intro, next). The problem scenes and the solution scenes are yours to write for each reel, because they are where the topic lives. Start from the closest example in `examples/`, keep its structure, and change the objects and copy.

## Examples

| File | Shape | Use it for |
| --- | --- | --- |
| `problem-diary-phone.html` | paper diary with crossed-out names + ringing phone with call cards + "not found" stamp | anything done on paper or by phone |
| `problem-waiting-room.html` | chairs, a bench of drawn people, a spinning wall clock, a speech bubble, one person walking out | waiting, crowds, lost customers |
| `problem-question-card.html` | a record card whose fields fill with red "?" then shakes | missing data, nobody remembers |
| `problem-board-flip.html` | a "Now Serving" board flipping numbers + a missed paper token stamped | something passing people by |
| `solution-phones-fan.html` | three app phones dealt into a fan, one per feature, a search that types | a role's 2–3 features (reception, staff) |
| `solution-earnings-chart.html` | two phones: a counting total with a bar chart, a staff bar list, a payment notification | owner/manager reports |
| `solution-whatsapp-chat.html` | a TV with a QR → push in, scan, lock → WhatsApp chat with buttons → a ticket flies out | any WhatsApp or chat flow |
| `solution-lockscreen-alert.html` | a lock screen with a status card that ticks, then a notification drops in | reminders, alerts |
| `solution-dashboard-click.html` | an admin card; a cursor clicks a button; rows swap; a mini TV and a phone update | one click updating several places |
| `cta-comment-keyword.html` | a document card with a FREE sticker + a comment box that types a keyword | "comment X to get Y" |
| `cta-free-link-bio.html` | struck-through objections, logo, a big button, "link bio mein ↓" | sign-up / free trial |

`problem-diary-phone.html` uses a handwriting font from `assets/fonts/`. On macOS copy `/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf` into the project for local use only (Apple fonts can't be redistributed), or download an open font such as Caveat (OFL) from Google Fonts into `assets/fonts/` and point the `@font-face` at it.

## Rules that kept the two reference reels clean

- **Key every reveal to its word.** `schedule.py` prints each caption word at its scene-local time (`booking@1.59`). Put the tween that shows a thing just before the word that names it (0.05–0.2 s early). A scene that animates on its own clock while the voice talks about something else reads as a slideshow.
- **One file, one scene.** The root is `#root` inside `<template>`; wrap everything in one `.clip` (`data-start="0"`, `data-duration` = the scene's `dur` from `.tx/sched.json`) with an inner `#<id>-in` div. Animate the inner div, never the `.clip` (HyperFrames forbids transforms on clips).
- **End with a 0.2 s fade of `#<id>-in`** starting at `dur - 0.22`, so cuts are clean.
- **Prefix every id with the scene id** (`#p2-bubble`). All scenes share one page.
- **Use `fromTo`.** For a second tween on the same element, use `tl.to(...)` or `immediateRender: false`, otherwise the check flags `gsap_repeated_fromto_without_baseline` and the element jumps on seek.
- **Reels layout (1080×1920):** nothing above y=168 (status bar), titles at y≈290–330, the main object between y≈420 and y≈1130, captions sit at y=1170, and everything below y=1330 is covered by the app's own caption and buttons. Keep text left of x≈930 below y≈770, where the like/comment rail sits.
- **Titles:** Archivo Black, one line. At 1080 px wide a line holds about 16 characters at 92 px, 19 at 76 px; size the title to its length, because a wrapped title slides under the object below it. two words of the title in the accent (or `#ff5a5f` red on problem scenes). Body: Inter 700–900. Labels: JetBrains Mono 700 with letter-spacing. Readable text is at least 28 px.
- **No emoji as icons.** Use an inline SVG or a drawn shape. Emoji inside a quoted message (a real WhatsApp text) are fine.
- **Show the product's real words.** For a real product, take button labels, notification text and screen names from its code or site, and mark sample data as such ("SAMPLE SCREENS").
- **Intended overlaps** (a ticket over a phone, a notification over a lock screen, a fan of phones): add `data-layout-allow-occlusion` on the covering element and `data-layout-allow-overlap` on the scene root, or the check reports `text_occluded`.
- **SVG files used in `<img>` need `xmlns="http://www.w3.org/2000/svg"`**, or they render as broken images.
