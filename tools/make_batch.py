#!/usr/bin/env python3
"""Print a generate_video_batch request list for runs FIRST..LAST, e.g. G10 G21.

Saved Higgsfield elements are written " @name " in the prompt; here each one
becomes the <<<element_id>>> placeholder the API expects (the backend injects
the element image and shows it as @name). Only non-element attachments
(start frames, the v4 bedroom plate) go in medias as image_references."""
import importlib.util, json, re, sys
s = importlib.util.spec_from_file_location("bp", "tools/build_prompts.py")
bp = importlib.util.module_from_spec(s); s.loader.exec_module(bp)
M = json.load(open("tools/element_media.json"))
E = bp.ELEMENTS
ids = [r["id"] for r in bp.RUNS]
a, b = ids.index(sys.argv[1]), ids.index(sys.argv[2])
out = []
for r in bp.RUNS[a:b + 1]:
    p, _ = bp.build(r)
    for h in sorted((h for h in r["attach"] if h in E), key=len, reverse=True):
        p = re.sub(rf"@{re.escape(h)}(?![A-Za-z0-9_-])", f"<<<{E[h]}>>>", p)
    assert "@" not in re.sub(r"@image\d+", "", p), (r["id"], "unresolved @tag")
    medias = ([{"role": "start_image", "value": M[r["start"]]}] if r.get("start") else []) \
        + [{"role": "image_references", "value": M[h]} for h in r["attach"] if h not in E] \
        + ([{"role": "end_image", "value": M[r["end"]]}] if r.get("end") else [])
    out.append({"index": int("".join(c for c in r["id"][1:] if c.isdigit())), "params": {"model": "seedance_2_5", "mode": "omni_reference", "draft": True,
        "resolution": "480p", "generate_audio": True, "aspect_ratio": "16:9", "duration": r["dur"],
        "folder_id": "92c8dd8a-7d90-4f19-9975-375b4becd001", "medias": medias, "prompt": p}})
print(json.dumps(out, ensure_ascii=False))
