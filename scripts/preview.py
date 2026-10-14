import sys
import numpy as np
import nibabel as nib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

t1_path, seg_path, out_path = sys.argv[1:4]
t1 = nib.as_closest_canonical(nib.load(t1_path)).get_fdata()
seg = nib.as_closest_canonical(nib.load(seg_path)).get_fdata().astype(int)

# Random but fixed colour per label
rng = np.random.default_rng(3)
labels = np.unique(seg)
lut = {l: rng.random(3) for l in labels if l != 0}

def overlay(t1s, segs):
    t = (t1s - t1s.min()) / (np.percentile(t1s, 99.5) - t1s.min() + 1e-6)
    rgb = np.repeat(np.clip(t, 0, 1)[..., None], 3, axis=2)
    col = np.zeros_like(rgb)
    for l, c in lut.items():
        col[segs == l] = c
    m = (segs > 0)[..., None]
    return np.where(m, 0.45 * rgb + 0.55 * col, rgb)

cx, cy, cz = [int(np.mean(np.nonzero(seg)[i])) for i in range(3)]
views = [
    ("Axial", t1[:, :, cz].T, seg[:, :, cz].T),
    ("Coronal", t1[:, cy, :].T, seg[:, cy, :].T),
    ("Sagittal", t1[cx, :, :].T, seg[cx, :, :].T),
]
fig, axes = plt.subplots(2, 3, figsize=(13, 9), facecolor="black")
for i, (name, a, s) in enumerate(views):
    axes[0, i].imshow(a, cmap="gray", origin="lower")
    axes[1, i].imshow(overlay(a, s), origin="lower")
    axes[0, i].set_title(f"{name}: T1 input", color="white")
    axes[1, i].set_title(f"{name}: SynthSeg labels", color="white")
for ax in axes.flat:
    ax.axis("off")
fig.suptitle(f"SynthSeg 2.0 (Neurodesk container) on OpenNeuro ds000001 sub-01: {len(lut)} labels",
             color="white", fontsize=13)
plt.tight_layout()
plt.savefig(out_path, dpi=110, facecolor="black")
print("saved", out_path)
