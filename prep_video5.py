"""Prepare video_5 data: keep first N frames, regenerate masks, clean tracks."""
import os, shutil, glob
import numpy as np
from PIL import Image

N = 20
SRC = "/tmp/v5extract/video_5/images"
BASE = "data/video_5"

dst = os.path.join(BASE, "images_3digit")
for f in os.listdir(dst):
    os.remove(os.path.join(dst, f))
files = sorted(os.listdir(SRC))
for i in range(N):
    shutil.copy2(os.path.join(SRC, files[i]), os.path.join(dst, f"{i:03d}.png"))
print(f"frames: {len(os.listdir(dst))}")

W, H = 640, 480
md = os.path.join(BASE, "motion_masks")
os.makedirs(md, exist_ok=True)
for f in os.listdir(md):
    os.remove(os.path.join(md, f))
cx, cy = W // 2, H // 2
rw, rh = int(W * 0.3), int(H * 0.3)
for i in range(N):
    mask = np.zeros((H, W), dtype=np.uint8)
    mask[cy - rh : cy + rh, cx - rw : cx + rw] = 255
    Image.fromarray(mask).save(os.path.join(md, f"{i:03d}.png"))
print(f"masks: {len(os.listdir(md))}")

for d in ["bootscotracker_dynamic", "bootscotracker_static", "uni_depth"]:
    p = os.path.join(BASE, d)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f"removed {p}")
print("Done prep_video5")
