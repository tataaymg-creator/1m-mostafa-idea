# LOOK — Handoff for the generating session

Paste the block below as the first message of a new session on this repository.

Before you start the session:

- Repository `tataaymg-creator/1m-mostafa-idea`, environment **1m-mostafa-idea** (it already allows the Higgsfield hosts).
- Higgsfield connector on and signed in to the account that holds the project **baba look**.

```text
Continue the film project LOOK on branch claude/wonderful-noether-yx6bsb. Do not open a pull request.

Read README.md, prompts.md and elements.md first. All prep is done: 33 elements are registered in the Higgsfield project "baba look", and prompts.md holds 49 ready generations (G01–G49), each with its elements, duration, aspect and full prompt.

Your job is generating only:
- Model Seedance 2.5, omni reference, draft ON, audio ON, into the project "baba look".
- For each run, attach exactly the elements listed, use the prompt text unchanged, and set the listed duration and aspect (4:3 or 16:9).
- Work in the batches I ask for, wait for them to finish, and show me the results in the gallery.
- Never finalise a draft to 1080p unless I say which ones.
- If a take fails, tell me what went wrong; do not rewrite the prompt without asking.
- Dialogue is English only. Mannequins never move on their own.

Start with G01 to G09 and show me the drafts.
```

## Where things stand

- **Done:** story, 87-shot list, 7 character and mannequin sheets, 12 location plates, 14 props, all registered as elements; 49 Seedance 2.5 prompts covering 82 shots.
- **Not done:** no video has been generated yet, so the prompts are untested.
- **Made in the edit, not generated:** shots 01, 64, 76, 86, 87 and the 4:3-to-16:9 widening on shot 77 (see the table in `prompts.md`).
- **Waiting on the director:** approval of the four fixed plates (kitchen, sewing corner, Nour's room, the two car plates).
- **Unverified:** the award deadline of 20 November 2026 and the other rules in `README.md`.

## Runs most likely to need retries

These involve a person handling a mannequin or an exact match, and are worth a stronger model if they keep failing: G10 and G28 (the carries), G16 (the dance), G17 and G18 (the arm), G37 (the eye match cut).

## Changing a prompt

Edit the run in `tools/build_prompts.py` and rebuild; timecodes are recalculated.

    python3 tools/build_prompts.py prompts.md prompts.html
