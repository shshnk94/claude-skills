# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy"]
# ///
"""Check that a palette's colours stay distinguishable under colour-vision deficiency
and in greyscale, and flag the pairs that become too similar.

Usage: uv run check_palette.py "#66C2A5" "#FC8D62" "#8DA0CB" [--threshold 10]

Simulates protanopia, deuteranopia and tritanopia (Machado et al. 2009, severity 1.0)
and greyscale, then compares every pair of colours with the CIEDE2000 colour
difference. Roughly: below 10 is hard to tell apart in a plot, below 5 nearly identical.
"""

import argparse
import itertools

import numpy as np

# Machado, Oliveira & Fernandes (2009) matrices, applied to linear RGB
CVD_MATRICES = {
    "protan": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    ),
    "deutan": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ]
    ),
    "tritan": np.array(
        [
            [1.255528, -0.076749, -0.178779],
            [-0.078411, 0.930809, 0.147602],
            [0.004733, 0.691367, 0.303900],
        ]
    ),
}
# linear sRGB -> XYZ (D65)
RGB_TO_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ]
)
D65_WHITE = np.array([0.95047, 1.0, 1.08883])


def hex_to_linear_rgb(hex_color: str) -> np.ndarray:
    """Convert '#RRGGBB' to linear RGB values between 0 and 1."""
    hex_color = hex_color.lstrip("#")
    srgb = np.array([int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]) / 255
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def linear_rgb_to_lab(linear_rgb: np.ndarray) -> np.ndarray:
    """Convert linear RGB to CIELAB under a D65 white point."""
    xyz = RGB_TO_XYZ @ np.clip(linear_rgb, 0, 1) / D65_WHITE
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def simulate(linear_rgb: np.ndarray, vision: str) -> np.ndarray:
    """Return how a linear RGB colour looks under the given vision type."""
    if vision == "normal":
        return linear_rgb
    if vision == "greyscale":
        luminance = RGB_TO_XYZ[1] @ linear_rgb
        return np.full(3, luminance)
    return CVD_MATRICES[vision] @ linear_rgb


def ciede2000(lab_1: np.ndarray, lab_2: np.ndarray) -> float:
    """CIEDE2000 colour difference between two CIELAB colours (Sharma et al. 2005)."""
    l1, a1, b1 = lab_1
    l2, a2, b2 = lab_2
    mean_chroma = (np.hypot(a1, b1) + np.hypot(a2, b2)) / 2
    g = 0.5 * (1 - np.sqrt(mean_chroma**7 / (mean_chroma**7 + 25**7)))
    a1_prime, a2_prime = a1 * (1 + g), a2 * (1 + g)
    c1, c2 = np.hypot(a1_prime, b1), np.hypot(a2_prime, b2)
    h1 = np.degrees(np.arctan2(b1, a1_prime)) % 360
    h2 = np.degrees(np.arctan2(b2, a2_prime)) % 360

    delta_l = l2 - l1
    delta_c = c2 - c1
    hue_gap = h2 - h1
    if c1 * c2 == 0:
        hue_gap = 0
    elif hue_gap > 180:
        hue_gap -= 360
    elif hue_gap < -180:
        hue_gap += 360
    delta_h = 2 * np.sqrt(c1 * c2) * np.sin(np.radians(hue_gap / 2))

    mean_l = (l1 + l2) / 2
    mean_c = (c1 + c2) / 2
    if c1 * c2 == 0:
        mean_h = h1 + h2
    elif abs(h1 - h2) <= 180:
        mean_h = (h1 + h2) / 2
    elif h1 + h2 < 360:
        mean_h = (h1 + h2 + 360) / 2
    else:
        mean_h = (h1 + h2 - 360) / 2

    t = (
        1
        - 0.17 * np.cos(np.radians(mean_h - 30))
        + 0.24 * np.cos(np.radians(2 * mean_h))
        + 0.32 * np.cos(np.radians(3 * mean_h + 6))
        - 0.20 * np.cos(np.radians(4 * mean_h - 63))
    )
    rotation_angle = 30 * np.exp(-(((mean_h - 275) / 25) ** 2))
    r_c = 2 * np.sqrt(mean_c**7 / (mean_c**7 + 25**7))
    s_l = 1 + 0.015 * (mean_l - 50) ** 2 / np.sqrt(20 + (mean_l - 50) ** 2)
    s_c = 1 + 0.045 * mean_c
    s_h = 1 + 0.015 * mean_c * t
    r_t = -np.sin(np.radians(2 * rotation_angle)) * r_c

    return float(
        np.sqrt(
            (delta_l / s_l) ** 2
            + (delta_c / s_c) ** 2
            + (delta_h / s_h) ** 2
            + r_t * (delta_c / s_c) * (delta_h / s_h)
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("colors", nargs="+", help="hex colours, e.g. '#66C2A5'")
    parser.add_argument("--threshold", type=float, default=10.0)
    args = parser.parse_args()

    visions = ["normal", "protan", "deutan", "tritan", "greyscale"]
    any_flagged = False
    for vision in visions:
        labs = {c: linear_rgb_to_lab(simulate(hex_to_linear_rgb(c), vision)) for c in args.colors}
        pair_distances = []
        for color_1, color_2 in itertools.combinations(args.colors, 2):
            pair_distances.append((ciede2000(labs[color_1], labs[color_2]), color_1, color_2))
        closest = min(pair_distances)
        flagged = [pair for pair in pair_distances if pair[0] < args.threshold]
        print(f"{vision:<10} closest pair dE={closest[0]:5.1f} ({closest[1]} vs {closest[2]})")
        for distance, color_1, color_2 in sorted(flagged):
            print(f"{'':<10}   too close: {color_1} vs {color_2} (dE={distance:.1f})")
        any_flagged = any_flagged or bool(flagged)

    if any_flagged:
        print(
            f"\nSome pairs fall below dE={args.threshold:g}. Separate them with direct "
            "labels, shapes, linetypes or panels, or swap a colour."
        )
    else:
        print(f"\nAll pairs stay at or above dE={args.threshold:g} in every simulation.")


if __name__ == "__main__":
    main()
