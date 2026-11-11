"""Build the animated v2 blocking (all runs, or the run ids given).

    blender -b -P build_v2.py
    blender -b -P build_v2.py -- G10 G16
    python build_v2.py G10            # with the bpy module
"""
import importlib
import os
import sys

import bpy  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import look_set  # noqa: E402
import apartment  # noqa: E402
import rig  # noqa: E402
import runs  # noqa: E402
for m in (look_set, apartment, rig, runs):
    importlib.reload(m)

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [a for a in sys.argv[1:] if not a.endswith(".py") and not a.startswith("-")]
for t in args or sorted(runs.RUNS):
    path, rep = runs.build(t, HERE)
    print("saved", os.path.basename(path))
    for line in rep:
        print("   ", line)
