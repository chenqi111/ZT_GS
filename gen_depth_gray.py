"""Generate grayscale (black-white) depth maps from rendered .npy depth files."""
import os
import numpy as np
from PIL import Image


def depth_to_grayscale(d, inv=False):
    """Map depth [H,W] to uint8 grayscale [H,W].
    inv=True: nearer=brighter (disparity-like), farther=darker."""
    valid = d > 0
    if not valid.any():
        return np.zeros(d.shape, dtype=np.uint8)
    dmin, dmax = np.percentile(d[valid], 1), np.percentile(d[valid], 99)
    g = np.clip((d - dmin) / max(dmax - dmin, 1e-8), 0, 1)
    if inv:
        g = 1.0 - g
    out = (g * 255).astype(np.uint8)
    out[~valid] = 0
    return out


def main():
    base = "output/video_5/render_results/depth"
    out_dir = "output/video_5/render_results/depth_gray"
    os.makedirs(out_dir, exist_ok=True)

    files = sorted([f for f in os.listdir(base) if f.endswith(".npy")])
    for f in files:
        d = np.load(os.path.join(base, f))
        gray = depth_to_grayscale(d, inv=False)
        Image.fromarray(gray, mode="L").save(os.path.join(out_dir, f.replace(".npy", ".png")))
    print(f"Generated {len(files)} grayscale depth maps -> {out_dir}")


if __name__ == "__main__":
    main()
