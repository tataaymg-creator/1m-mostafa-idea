# LOOK — Handoff (generation history, state as of 2026-11-12)

> **2026-11-13: generation is finished. For the edit, read [HANDOFF-EDIT.md](HANDOFF-EDIT.md): the final 38 clips in 1080p, in cut order, with cut points.** The rest of this file is the generation log.

Short film for the 1 Billion Followers Summit AI Film Award. Repo branch `claude/wonderful-noether-yx6bsb`. Higgsfield project **baba look** (folder `92c8dd8a-7d90-4f19-9975-375b4becd001`).

## How to continue
Open a new session on this repository and paste:

```text
Continue the film LOOK on branch claude/wonderful-noether-yx6bsb exactly from where we stopped. Read HANDOFF.md first, then tools/build_prompts.py, tools/make_batch.py and tools/element_media.json. All 49 shots have drafts; we are in the review / fix pass. Follow the rules in HANDOFF.md. Reply to me in Egyptian Arabic, keep it short, watch every draft yourself (ffmpeg contact sheets) before sending it, and send videos with SendUserFile. Commit and push after each change. No pull request. Wait for my next note.
```

## Rules (from the user)
- Seedance 2.5 **Draft** only (`seedance_2_5`, `mode: omni_reference`, `draft: true`, 480p, audio on), **16:9**. Finalise to 1080p (`draft_job_id`) only when the user names the drafts.
- Prompts follow the seedance-clean structure; build them with `python3 -B tools/build_prompts.py prompts.md prompts.html` and the request JSON with `python3 -B tools/make_batch.py G28 G28` (supports `start=` → `start_image`, `end=` → `end_image`, ids like `G15a`).
- English dialogue only. **No generated music** (it triggers `ip_detected`): write "The score is laid in during the edit."
- Be a problem solver: if a shot keeps failing, change the action or the staging; the meaning matters, not the letter of the script.
- Never merge other branches.

## Lessons that work
- **Elements work in Seedance 2.5.** In the Higgsfield UI write ` @name ` (space before @ and after the name). Through the API put `<<<element_id>>>` in the prompt and leave `mode` out (omni_reference demands a media item and rejects element-only runs). `build_prompts.py` writes ` @name `; `make_batch.py` turns it into the placeholder. Ids in `tools/element_ids.json` (`L06_nour-room` is excluded: the saved element still holds the old plate, so the v4 plate goes in as an image reference).
- Lock placement with a **start frame** (extract a frame from an approved take, or edit the location plate by *adding* a person/prop). `end_image` also works.
- A take that is good except one detail → **`mode: video_edit`** with the take as `video_references` (fixed G37's glowing eyes without losing the take).
- Location plates must have real geometry. The bedroom was rebuilt from an exact perspective blocking (`tools/room_blocking.py` → `locations/L06_blocking.png`), rendered from the blocking ALONE (attaching the old photo makes the model copy it). Check plates by overlaying the blocking edges.
- Costume changes need their own reference: mother mannequin after G44 = `doll-wife-bare` (`characters/06b-mannequin-adult-no-cardigan.png`, grey dress). A bare plastic torso is refused as NSFW.
- Avoid on-camera actions that keep breaking (laying the mannequin on the bed) — cut around them.

## Current takes (latest draft per shot)
G01–G03: approved earlier (check the baba look folder). G04 41d0f3e0 · G05 a3c251ee · G06 9081951b · G07 fc95918b · G08 d58f1d5c · G09 c5a1599d · G10 a0c5b8dc · G11 88d4b73f · G12 4a61618b · G13 18ce6352 · G14 2b4009ce · G15 3a2554e0 (segments 2–3 mirrored in edit) + **G15a 72b5cc86** (radio insert, hand from the passenger side) · G16 31efcdb6 · G17 9fe9dba0 · G18 1d720a85 · G19 2cf11c7f · G20 221cf3da · G21 917293a7 · G22 6e8ca41d · G23 ecdce175
G24 fed778a7 · G25 4d694069 (dinner — **flagged**, revisit) · G26 merged into G25
G27 — **not generated**: cut from G35 (Layla 0–1.4 s + truck 2.6–3.9 s + 0.5 s fade to white)
G28 5281b684 (corridor: he carries her toward the doorway camera and passes it) → G29 fe2c6c1d (tuck-in, kiss, leaves) → G30 a41bfe89 — no shot of laying her down
G31 5fdb8f2e · G32 059f4173 · G33 5abfeb16 · G34 **1b465623** (approved: real drawing, truck head-on) · G35 8aa391e4 · G36 c76936d3
G37 **41bdd36a** (original take 1ee87ab2 with the eye glow removed by video_edit)
G38 c4d92076 (start F38_bed e82a1245) · G39 9b8ba5d8 (crying; user thinks it is weak) + G39b 6c18dc34 (dawn wide, start F39_wide)
G40 **b16bd237** (approved) · G41 bb1c9720 · G42 bf11d1e5 + **G42b 9c30858b** (approved: from the last G41 frame, drawing revealed, "I'm looking, sweetheart") · G43 706da129 · G44 b4cf79ce (kept as two shots; the one-take idea was dropped) · G45 dropped by the user · G46 26784890 · G47 **2fcc33c6** (OK; cut it as he heads for the door) · G48 **6aada38e** (approved) · G49 → **G49k 42387b13** (kitchen hug, approved; replaces the doorway versions)

## Open items
- G24/G25 dinner (flagged by the user).
- G39 crying shot: user said it is weak; decide whether to redo it (mannequin visible in bed, longer).
- G28 corridor: the amber glow from the room is faint; offer a brighter version if asked.
- Bedroom plate `L06_nour-room` = v4 (5ca61ad1). Footboard reads tall; lower it in `tools/room_blocking.py` if the user asks.
- Remote branches `claude/ecstatic-goodall-fjoxzr` and `claude/fervent-lovelace-vdi740` must be deleted by the user in the GitHub UI.

## Files
`tools/build_prompts.py` (all runs) · `tools/make_batch.py` · `tools/element_media.json` (element → Higgsfield id) · `tools/room_blocking.py` · `prompts.md` / `prompts.html` · `elements.md` · `locations/` (plates and start frames) · `characters/` · `props/`
