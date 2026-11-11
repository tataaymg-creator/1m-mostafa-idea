"""Builds B11_car-from-back-seat_G32_v1.blend next to this script.
    blender -b -P blocking_B11_car-from-back-seat_G32_v1.py
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
print(shots.build("B11_car-from-back-seat_G32")[0])
