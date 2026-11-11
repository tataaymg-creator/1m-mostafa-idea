"""Build every blocking .blend (or the tags given after --).

    blender -b -P build_all.py                      # all
    blender -b -P build_all.py -- B05a_living-wide_G10
    python build_all.py B05a_living-wide_G10       # with the bpy module
"""
import importlib

import bpy  # noqa: F401
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import look_set  # noqa: E402
import apartment  # noqa: E402
import shots  # noqa: E402
for m in (look_set, apartment, shots):
    importlib.reload(m)

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [a for a in sys.argv[1:] if not a.endswith(".py") and not a.startswith("-")]
tags = args or list(shots.SH)
for t in tags:
    path, report = shots.build(t, HERE)
    print("saved", os.path.basename(path))
    for line in report:
        print("   ", line)
