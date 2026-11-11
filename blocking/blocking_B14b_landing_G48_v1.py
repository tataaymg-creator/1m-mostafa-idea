"""Builds B14b_landing_G48_v1.blend next to this script.
    blender -b -P blocking_B14b_landing_G48_v1.py
"""
import os
import sys

import bpy  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib  # noqa: E402

import look_set  # noqa: E402
import apartment  # noqa: E402
import shots  # noqa: E402
for m in (look_set, apartment, shots):
    importlib.reload(m)
print(shots.build("B14b_landing_G48")[0])
