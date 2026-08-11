#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Plot phonon band structure from matdyn.x output, reading the high-symmetry
q-point path (labels + points-per-segment) directly from the matdyn.x input
file instead of hardcoding indices/labels in the plotting script.

Usage:
    python plot_phonon_bands.py name.in
    (if no argument is given, it auto-detects the single *.in file
    in the current directory — any filename works, e.g. matdyn.in,
    diamond.in, name.in)

    Add --split to plot each frequency (band) column in its own color:
    python plot_phonon_bands.py name.in --split
"""

import argparse
import glob
import re
import numpy as np
import matplotlib.pyplot as plt


def find_input_file():
    """
    Locate the matdyn.x input file when the user doesn't name it explicitly.
    Any file ending in .in in the current directory qualifies (e.g. name.in,
    matdyn.in, diamond.matdyn.in) — no fixed filename is assumed.
    """
    candidates = sorted(glob.glob("*.in"))
    if not candidates:
        raise FileNotFoundError(
            "No .in file found in the current directory. "
            "Pass the path explicitly: python plot_phonon_bands.py <file.in>"
        )
    if len(candidates) > 1:
        raise ValueError(
            f"Multiple .in files found: {candidates}. "
            "Pass the one to use explicitly: python plot_phonon_bands.py <file.in>"
        )
    return candidates[0]


def parse_matdyn_input(filename):
    """
    Parse a matdyn.x input file (q_in_band_form = .true.) to extract:
      - flfrq  : the frequency output file prefix (namelist variable)
      - labels : high-symmetry point labels (from the "! label" comments)
      - npts   : number of points requested for each segment (4th column)

    Assumes the standard band-path format:
        &INPUT ... /
        <nq>
        qx qy qz npts   ! Label
        ...
    """
    with open(filename) as f:
        lines = f.readlines()

    # --- flfrq from the namelist ---
    flfrq = None
    for line in lines:
        m = re.search(r"flfrq\s*=\s*['\"]([^'\"]+)['\"]", line)
        if m:
            flfrq = m.group(1)

    # --- locate end of namelist ---
    end_idx = next(i for i, l in enumerate(lines) if l.strip() == "/")

    # --- number of q-points ---
    nq = int(lines[end_idx + 1].split()[0])

    labels, npts_list = [], []
    for line in lines[end_idx + 2: end_idx + 2 + nq]:
        body, _, comment = line.partition("!")
        cols = body.split()
        npts_list.append(int(cols[3]))
        labels.append(comment.strip())

    return flfrq, labels, npts_list


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot a phonon band structure from matdyn.x output."
    )
    parser.add_argument(
        "input_file", nargs="?", default=None,
        help="matdyn.x input file (e.g. name.in). If omitted, auto-detects "
             "the single *.in file in the current directory.",
    )
    parser.add_argument(
        "--split", action="store_true",
        help="Plot each frequency (band) column in its own color instead "
             "of uniform black.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    matdyn_input = args.input_file if args.input_file else find_input_file()

    flfrq, labels, npts_list = parse_matdyn_input(matdyn_input)
    if flfrq is None:
        raise ValueError(f"Could not find flfrq in {matdyn_input}")

    gp_file = f"{flfrq}.gp"
    data = np.loadtxt(gp_file)
    nbands = data.shape[1] - 1

    # matdyn.x writes frequencies in cm^-1 by default; convert to THz.
    # 1 cm^-1 = c[cm/s] * 1e-12 = 0.0299792458 THz
    CM1_TO_THZ = 0.0299792458
    data[:, 1:] *= CM1_TO_THZ

    # Cumulative row index of each high-symmetry point in the .gp file.
    # matdyn writes npts points for each segment except the last q-point,
    # whose "npts" column is unused (that point is just the path endpoint).
    indices = [0]
    for n in npts_list[:-1]:
        indices.append(indices[-1] + n)
    indices[-1] = data.shape[0] - 1  # guard against off-by-one mismatches

    tick_positions = data[indices, 0]
    tick_labels = [r"$\Gamma$" if lab.upper() in ("G", "GAMMA") else lab
                   for lab in labels]

    fig, ax = plt.subplots()
    if args.split:
        colors = plt.cm.tab20(np.linspace(0, 1, nbands)) if nbands > 10 \
            else plt.cm.tab10(np.linspace(0, 1, nbands))
        for band in range(nbands):
            ax.plot(data[:, 0], data[:, band + 1], linewidth=1,
                    color=colors[band], label=f"Band {band + 1}")
        ax.legend(fontsize="small", ncol=2, loc="best")
    else:
        for band in range(nbands):
            ax.plot(data[:, 0], data[:, band + 1], color="xkcd:blue") # , linewidth=1, alpha=0.5

    for x in tick_positions:
        ax.axvline(x=x, linewidth=0.5, color="k", alpha=0.5)

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)
    ax.set_ylabel("Frequency (THz)")
    ax.set_xlim(data[0, 0], data[-1, 0])
    ax.set_ylim(0, None)
    fig.tight_layout()
    fig.savefig("phonon_band.png", dpi=150)


if __name__ == "__main__":
    main()
