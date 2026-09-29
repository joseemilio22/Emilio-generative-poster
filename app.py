# Week 5 - Interactive Generative Poster (Streamlit version)
# Variation: red palette + circles orbiting a central Canon AE-1
# Concepts: from Colab notebook to web app
# Change from Colab: ipywidgets `interact` -> Streamlit sidebar widgets

import os, random, math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import streamlit as st

# Poster canvas (figure is 6x8, so x runs 0-1 and y runs 0-4/3 -> true circles)
W, H = 1.0, 4 / 3
CAM_CENTER = (W / 2, H / 2)
CAM_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera.png")


# Circle shape (replaces the wobbly blob).
# draw_poster() still hands us a random centre + radius; here we steer that
# centre onto a ring around the camera so every circle orbits it.
# `wobble` now controls how loosely the circles are spread around the ring.
def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    dx, dy = center[0] - 0.5, center[1] - 0.5
    angle = math.atan2(dy, dx)
    dist = min(math.hypot(dx, dy) / 0.707, 1.0)          # 0 (middle) .. 1 (corner)
    orbit = 0.32 + 0.22 * dist + wobble * (np.random.rand() - 0.5)
    cx = CAM_CENTER[0] + orbit * math.cos(angle) * 0.85   # squeeze ring so circles stay in frame
    cy = CAM_CENTER[1] + orbit * math.sin(angle) * 1.15  # slightly taller ring
    rad = r * 0.6
    angles = np.linspace(0, 2 * math.pi, points, endpoint=False)
    x = cx + rad * np.cos(angles)
    y = cy + rad * np.sin(angles)
    return x, y


# Red palette generator (HSV): every mode stays in the red family
def make_palette(k=6, mode="pastel", base_h=0.99):
    cols = []
    for _ in range(k):
        if mode == "pastel":      # blush / rose / peach
            h = (random.uniform(-0.04, 0.05)) % 1
            s = random.uniform(0.15, 0.40); v = random.uniform(0.92, 1.0)
        elif mode == "vivid":     # scarlet / crimson / cherry
            h = (random.uniform(-0.03, 0.03)) % 1
            s = random.uniform(0.80, 1.0); v = random.uniform(0.75, 1.0)
        elif mode == "mono":      # one red, different depths
            h = base_h
            s = random.uniform(0.3, 0.9); v = random.uniform(0.45, 1.0)
        else:  # random: warm reds drifting toward coral and magenta
            h = (random.uniform(-0.07, 0.07)) % 1
            s = random.uniform(0.5, 1.0); v = random.uniform(0.6, 1.0)
        cols.append(tuple(hsv_to_rgb([h, s, v])))
    return cols


# Finishing touches applied to the figure AFTER draw_poster() returns, so
# draw_poster() itself stays untouched: fixed canvas, clean circle edges,
# warm backdrop, then the camera in the middle on top of a soft halo.
def finish_poster(fig):
    ax = fig.axes[0]
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    # newer matplotlib lets color= override edgecolor=, so strip the outlines here
    for p in ax.patches:
        p.set_edgecolor("none")
    ax.add_patch(plt.Rectangle((0, 0), W, H, facecolor=(0.99, 0.96, 0.94),
                               edgecolor="none", zorder=-1))
    cx, cy = CAM_CENTER
    t = np.linspace(0, 2 * math.pi, 200)
    for k, a in [(1.00, 0.20), (0.85, 0.25), (0.70, 0.35)]:   # layered soft glow
        ax.fill(cx + 0.40 * k * np.cos(t), cy + 0.30 * k * np.sin(t),
                facecolor=(1, 1, 1), alpha=a, edgecolor="none", zorder=5)
    cw = 0.60                                   # camera width on the poster
    img = plt.imread(CAM_PATH)
    ch = cw * img.shape[0] / img.shape[1]
    ax.imshow(img, extent=[cx - cw / 2, cx + cw / 2, cy - ch / 2, cy + ch / 2],
              zorder=10, interpolation="lanczos")


# Main drawing function: returns a figure instead of calling plt.show()
def draw_poster(n_layers=8, wobble=0.15, palette_mode="pastel", seed=0):
    random.seed(seed)
    np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.axis("off")
    ax.set_facecolor((0.97, 0.97, 0.97))

    palette = make_palette(6, mode=palette_mode)
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        x, y = blob((cx, cy), r=rr, wobble=wobble)
        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.6)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0, 0, 0, 0))


    ax.text(0.05, 0.95, f"Interactive Poster • {palette_mode}",
            transform=ax.transAxes, fontsize=12, weight="bold")
    return fig


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Interactive Generative Poster", layout="centered")
st.title("Interactive Generative Poster")
st.caption("Arts and Advanced Big Data | From Colab to the Web")

st.sidebar.header("Controls")
n_layers = st.sidebar.slider("Layers", min_value=3, max_value=20, value=8, step=1)
wobble = st.sidebar.slider("Wobble", min_value=0.01, max_value=0.30, value=0.15, step=0.01)
palette_mode = st.sidebar.selectbox("Palette mode", ["pastel", "vivid", "mono", "random"])
seed = st.sidebar.slider("Seed", min_value=0, max_value=9999, value=0, step=1)

fig = draw_poster(n_layers, wobble, palette_mode, seed)
finish_poster(fig)
st.pyplot(fig)
