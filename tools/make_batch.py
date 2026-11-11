#!/usr/bin/env python3
"""Print a generate_video_batch request list for runs FIRST..LAST, e.g. G10 G21."""
import importlib.util, json, sys
s = importlib.util.spec_from_file_location("bp", "tools/build_prompts.py")
bp = importlib.util.module_from_spec(s); s.loader.exec_module(bp)
M = json.load(open("tools/element_media.json"))
ids = [r["id"] for r in bp.RUNS]
a, b = ids.index(sys.argv[1]), ids.index(sys.argv[2])
out = []
for r in bp.RUNS[a:b + 1]:
    p, _ = bp.build(r)
    out.append({"index": int(r["id"][1:]), "params": {"model": "seedance_2_5", "mode": "omni_reference", "draft": True,
        "resolution": "480p", "generate_audio": True, "aspect_ratio": "16:9", "duration": r["dur"],
        "folder_id": "92c8dd8a-7d90-4f19-9975-375b4becd001",
        "medias": ([{"role": "start_image", "value": M[r["start"]]}] if r.get("start") else []) + [{"role": "image_references", "value": M[h]} for h in r["attach"]], "prompt": p}})
print(json.dumps(out, ensure_ascii=False))
