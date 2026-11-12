# LOOK — Handoff


Paste this as the first message of a new session on this repository (environment **1m-mostafa-idea**, Higgsfield connected to the account with the project **baba look**):

```text
Continue the film project LOOK on branch claude/wonderful-noether-yx6bsb from where we stopped: everything is prepared and the next step is generating.

Read prompts.md and elements.md. The 32 elements in use are registered in the Higgsfield project "baba look", and prompts.md has the 49 runs (G01–G49) with their elements, duration and full prompt.

Generate with Seedance 2.5 Draft, 16:9, audio on, into "baba look". Attach the element images for each run in the order listed (the first is @image1, the second @image2, and so on) and use the prompt unchanged. Show me the drafts; I choose which to generate again in 1080p. Do not open a pull request.

Start with G01 to G09.
```

## Flagged — revisit later
- **G24 + G25 (dinner: cup knock and low-angle lamp flicker).** The user flagged these to come back to. Latest drafts: G24 `fed778a7`, G25 `4d694069`. Start frames: `locations/F24_cup.png`, `locations/F25_low.png`.

## Latest drafts (G34–G49)
G34 fb52bb1a · G35 8aa391e4 · G36 c76936d3 · G37 1ee87ab2 · G38 20ea3b97 · G39 216b6142 · G40 706c152d · G41 0b32f714 · G42 bf11d1e5 · G43 706da129 · G44 19e7cd7d · G45 b29fe51a · G46 26784890 · G47 f0218e45 · G48 df27c838 · G49 c93b8b35

## Edit pass — done
Redone and checked: G37 3232ee7d (natural eye) · G38 336f5cc0 (tuck-in pose, start F38_bed) · G41 bb1c9720 (clear bag) · G44 b4cf79ce (starts on F43_end; cardigan off shows grey dress) · G45 141f7886 (on the sofa, mother in grey dress).
Continuity rule: after G44 the mother mannequin is `doll-wife-bare` (grey dress, no cardigan), reference `characters/06b-mannequin-adult-no-cardigan.png`.
G36 crayon accepted as is.

## G22 / G27 / G28
- G22 6e8ca41d — approved.
- G27 — not generated. Cut in the edit from G35: Layla 0.0–1.4s + truck 2.6–3.9s + 0.5s fade to white (3.1s). Same truck, light and Layla as the crash.
- G28 02cf7379 — locked wide built on the FIXED L06 plate (start `locations/F28_start.png`, job 109fba97): he carries her from the rug to the bedside, standing. G29 then starts with her on the bed. Laying her down on camera kept breaking (wrong orientation, camera drift), so it is left between the cut.

## Bedroom plate fixed
`locations/L06_nour-room_v2.png` (Higgsfield 39f98068) replaces the old plate, whose bed was warped (mattress wider than the footboard, a loose leg). The old file is kept as `locations/L06_nour-room_old-warped-bed.jpg`. Every bedroom shot generated from now on uses the fixed plate. Already-approved G29/G30 were made on the old plate; if they read differently in the cut, regenerate them on v2.

## Bedroom plate v4 (geometry-locked)
v3 had no ceiling in the blocking, so the model invented a broken one. v4 (`locations/L06_nour-room_v4.png`, 57cb6223 -> now 5ca61ad1) uses a level camera, a visible ceiling, a cornice and a skirting band in the blocking. `L06_nour-room` points to v4.

### (older note) v3
The v2 fix still had broken walls. v3 (`locations/L06_nour-room_v3.png`, Higgsfield 57cb6223) is rendered from an exact perspective blocking built in `tools/room_blocking.py` (`locations/L06_blocking.png`, real metres, one camera). Render it from the blocking ALONE: when the old photo is also attached, the image model copies the old photo and ignores the blocking. `L06_nour-room` now points to v3. Pending: user approval, then redo the G28 start frame and every bedroom shot on v3.

## Bedroom shots on plate v4 (done)
G28 f253a420 (start F28_start 92e93a22) · G29 fe2c6c1d · G30 a41bfe89 · G38 c4d92076 (start F38_bed e82a1245, pose from G29 at 5.5s) · G39 9b8ba5d8 (use 0–15 s, the crying) + G39b 6c18dc34 (dawn wide, start F39_wide 4fa14d9f).
G37 kept as 3232ee7d: its bedroom half is an extreme close-up of the eye on the terrazzo floor, so the plate never shows.

## Bedtime order (user decision)
G28 5281b684 (he carries her down the corridor toward the doorway camera and passes it) → hard cut → G29 fe2c6c1d (tuck-in, kiss, he leaves). No shot of him laying her down.
