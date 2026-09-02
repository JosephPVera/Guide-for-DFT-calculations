#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Usage:
    python3 s_bandplot.py [--y] [--nres]

SIESTA .bands file layout:
    line 1        : Fermi energy (eV)
    line 2        : kmin  kmax  Emin  Emax
    line 3        : nbands  nspin  nkpoints
    next block    : for each k-point ->
                       k_distance  E_1 E_2 ... E_nbands   (nspin=1)
                       k_distance  E_1 ... E_nbands E_1 ... E_nbands  (nspin=2)
    final block   : n_labels
                     k_distance_1  'label_1'
                     ...
                     k_distance_n  'label_n'
"""

import argparse
import glob
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_FILE = "band_structure.png"

def find_bands_file() -> str:
    """Automatically locate the .bands file in the current directory."""
    candidates = sorted(glob.glob("*.bands"))
    if not candidates:
        sys.exit("Error: no '*.bands' file found in the current directory.")
    if len(candidates) > 1:
        print(f"Warning: multiple .bands files found, using '{candidates[0]}'.")
        print(f"         (all candidates: {candidates})")
    return candidates[0]

def parse_bands_file(path: str):
    """Parse a SIESTA .bands file.
    e_fermi : float
    kmin, kmax, emin, emax : float
    nbands : int
    nspin : int
    nkpts : int
    kpath : np.ndarray, shape (nkpts,)
    bands : np.ndarray, shape (nspin, nkpts, nbands)
    labels : list[(float, str)]
    """
    with open(path, "r") as f:
        tokens = f.read().split()

    idx = 0

    e_fermi = float(tokens[idx]); idx += 1
    kmin = float(tokens[idx]); idx += 1
    kmax = float(tokens[idx]); idx += 1
    emin = float(tokens[idx]); idx += 1
    emax = float(tokens[idx]); idx += 1

    nbands = int(tokens[idx]); idx += 1
    nspin = int(tokens[idx]); idx += 1
    nkpts = int(tokens[idx]); idx += 1

    n_per_kpoint = nspin * nbands

    kpath = np.empty(nkpts)
    bands = np.empty((nspin, nkpts, nbands))

    for ik in range(nkpts):
        kpath[ik] = float(tokens[idx]); idx += 1
        values = tokens[idx: idx + n_per_kpoint]
        idx += n_per_kpoint
        values = np.array(values, dtype=float)
        if nspin == 1:
            bands[0, ik, :] = values
        else:
            bands[0, ik, :] = values[:nbands]
            bands[1, ik, :] = values[nbands:]

    labels = []
    if idx < len(tokens):
        n_labels = int(tokens[idx]); idx += 1
        remainder = " ".join(tokens[idx:])
        pattern = re.findall(r"([-\d.]+)\s+'([^']*)'", remainder)
        for dist_str, name in pattern[:n_labels]:
            labels.append((float(dist_str), name))

    return {
        "e_fermi": e_fermi,
        "kmin": kmin,
        "kmax": kmax,
        "emin": emin,
        "emax": emax,
        "nbands": nbands,
        "nspin": nspin,
        "nkpts": nkpts,
        "kpath": kpath,
        "bands": bands,
        "labels": labels,
    }

def classify_and_get_reference(bands: np.ndarray, e_fermi: float, tol: float = 1e-4):
    """Decide whether the system is a metal or a semiconductor/insulator and
    return the energy reference to use for the plot"""
    all_energies = bands.reshape(-1)

    occupied = all_energies[all_energies <= e_fermi]
    unoccupied = all_energies[all_energies > e_fermi]

    if occupied.size == 0 or unoccupied.size == 0:
        return e_fermi, False, None, None

    vbm = occupied.max()
    cbm = unoccupied.min()

    is_semiconductor = (cbm - vbm) > tol

    if is_semiconductor:
        return vbm, True, vbm, cbm
    return e_fermi, False, vbm, cbm

def plot_bands(data, out_path: str, yrange, no_rescale: bool = False):
    kpath = data["kpath"]
    bands = data["bands"]
    nspin = data["nspin"]
    labels = data["labels"]
    e_fermi = data["e_fermi"]

    if no_rescale:
        print("  --nres flag set -> no rescaling applied, plotting raw energies.")
        reference = 0.0
        ylabel = "E (eV)"
    else:
        reference, is_semiconductor, vbm, cbm = classify_and_get_reference(bands, e_fermi)

        if is_semiconductor:
            gap = cbm - vbm
            print(f"  Detected a gap at E_F ({gap:.6f} eV) -> treating as semiconductor/insulator.")
            print(f"  VBM = {vbm:.6f} eV, CBM = {cbm:.6f} eV. Rescaling energies to E - E_VBM.")
            ylabel = "E - E$_{VBM}$ (eV)"
        else:
            print("  No gap found at E_F -> treating as metal. Rescaling energies to E - E_F.")
            ylabel = "E - E$_F$ (eV)"

    fig, ax = plt.subplots() 

    spin_colors = ["tab:blue", "tab:red"]
    spin_names = ["up", "down"]

    for ispin in range(nspin):
        color = spin_colors[ispin] if nspin > 1 else "xkcd:blue"
        for ib in range(bands.shape[2]):
            energies = bands[ispin, :, ib] - reference
            label = None
            if nspin > 1 and ib == 0:
                label = f"spin {spin_names[ispin]}"
            ax.plot(kpath, energies, color=color, lw=0.9, label=label)

    ax.axhline(0.0, color="xkcd:black", ls="--", lw=0.8)

    # High-symmetry point vertical lines and x-tick labels
    if labels:
        greek_map = {"gamma": "\u0393", "delta": "\u0394", "sigma": "\u03a3", "lambda": "\u039b"}
        xt = [d for d, _ in labels]
        xl = [greek_map.get(name.lower(), name) for _, name in labels]
        for d in xt:
            ax.axvline(d, color="xkcd:gray", lw=0.4)
        ax.set_xticks(xt)
        ax.set_xticklabels(xl, fontsize=10)

    ax.set_xlim(kpath.min(), kpath.max())

    if yrange is not None:
        ax.set_ylim(yrange[0], yrange[1])
    else:
        ax.set_ylim(data["emin"] - reference, data["emax"] - reference)

    ax.set_ylabel(ylabel, fontsize=14)
    #ax.set_title("Band structure")

    if nspin > 1:
        ax.legend(loc="best", fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=300)

def main():
    parser = argparse.ArgumentParser(description="Plot a SIESTA band structure (.bands file).")
    parser.add_argument("--y", nargs=2, type=float, metavar=("YMIN", "YMAX"),
                         help="Y-axis range in eV, e.g. --y -10 15. "
                              "If omitted, the range from the .bands file is used.")
    parser.add_argument("--nres", action="store_true",
                         help="Disable rescaling in all cases (plot raw energies from the file). "
                              "By default, rescaling is always applied.")
    args = parser.parse_args()

    bands_file = find_bands_file()
    print(f"Reading: {bands_file}\n")

    data = parse_bands_file(bands_file)

    plot_bands(data, out_path=OUTPUT_FILE, yrange=args.y, no_rescale=args.nres)

if __name__ == "__main__":
    main()
