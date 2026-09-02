#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Plot an Elk band structure from BAND.OUT, using the high-symmetry point
positions from BANDLINES.OUT and the point labels from the plot1d block
in elk.in.

The only manual input required is VBM_HA: Elk prints energies as E - E_F,
so this script needs to know where the valence band maximum sits relative
to that shift in order to re-reference the plot to E - E_VBM = 0.
"""

import argparse
import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt

BAND_FILE = 'BAND.OUT'
BANDLINES_FILE = 'BANDLINES.OUT'
ELK_IN_FILE = 'elk.in'
OUTPUT_FILE = 'bandstructure.png'

HA_TO_EV = 27.21138624598
OCC_THRESHOLD = 1e-3  # occupancy above this is considered "occupied", same convention as elk_gap.py / elk_dos.py

def read_fermi_energy(filename):
    """Read the Fermi energy (Ha) from an ELK EFERMI.OUT file"""
    with open(filename) as fh:
        first_line = fh.readline()
    try:
        return float(first_line.split()[0])
    except (IndexError, ValueError):
        sys.exit(f"Error: could not parse a Fermi energy from {filename}.")

def find_vbm(filename):
    """Read an ELK EIGVAL.OUT file and return the VBM (Ha)"""
    line_re = re.compile(
        r"^\s*\d+\s+([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s+"
        r"([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s*$"
    )

    occupied = []
    with open(filename) as fh:
        for line in fh:
            m = line_re.match(line)
            if m:
                eigenvalue = float(m.group(1))
                occupancy = float(m.group(2))
                if occupancy > OCC_THRESHOLD:
                    occupied.append(eigenvalue)

    if not occupied:
        sys.exit(f"Error: no occupied states found in {filename} "
                  f"(check OCC_THRESHOLD).")

    return max(occupied)

def get_vbm_minus_ef(scf_dir):
    """Return VBM - E_F (Ha), reading EIGVAL.OUT and EFERMI.OUT from scf_dir."""
    eigval_file = os.path.join(scf_dir, "EIGVAL.OUT")
    efermi_file = os.path.join(scf_dir, "EFERMI.OUT")

    if not os.path.isfile(eigval_file):
        sys.exit(f"Error: {eigval_file} not found.")
    if not os.path.isfile(efermi_file):
        sys.exit(f"Error: {efermi_file} not found.")

    vbm_ha = find_vbm(eigval_file)
    ef_ha = read_fermi_energy(efermi_file)
    return vbm_ha - ef_ha

# Common high-symmetry point names 
GREEK_LABELS = {
    'gamma': r'$\Gamma$',
    'delta': r'$\Delta$',
    'lambda': r'$\Lambda$',
    'sigma': r'$\Sigma$',
    'theta': r'$\Theta$',
    'omega': r'$\Omega$',
    'pi': r'$\Pi$',
    'phi': r'$\Phi$',
    'psi': r'$\Psi$',
    'xi': r'$\Xi$',
}

def format_label(label):
    """Turn a raw high-symmetry point name into a nicely formatted label."""
    key = label.strip().lower()
    return GREEK_LABELS.get(key, label.strip())

def read_bands(band_file):
    """Read BAND.OUT and return the k-path array and energies (Ha)."""
    data = np.loadtxt(band_file)
    k = np.unique(data[:, 0])          # k-path distance is sorted, ascending
    nk = len(k)
    bands = np.reshape(data[:, 1], (-1, nk))
    return k, bands

def read_high_symmetry_positions(bandlines_file):
    """Read BANDLINES.OUT and return the x-position of each vertical line."""
    data = np.loadtxt(bandlines_file)
    return np.unique(data[:, 0])

def read_labels_from_elkin(elk_in_file):
    """Parse the plot1d block of elk.in and return the point labels, in
    order, taken from the text after ':' on each k-point line."""
    with open(elk_in_file, 'r') as f:
        lines = [ln.rstrip('\n') for ln in f]

    labels = []
    i = 0
    while i < len(lines):
        if lines[i].strip().lower() == 'plot1d':
            j = i + 1
            while lines[j].strip() == '':
                j += 1
            nlines = int(lines[j].split()[0])   # first number = # of k-points
            j += 1
            count = 0
            while count < nlines and j < len(lines):
                if lines[j].strip() == '':
                    j += 1
                    continue
                parts = lines[j].split(':', 1)
                labels.append(format_label(parts[1]) if len(parts) == 2 else '')
                count += 1
                j += 1
            break
        i += 1
    return labels

def main():
    parser = argparse.ArgumentParser(description="Plot Elk band structure (Ha -> eV).")
    parser.add_argument("--scf-dir", type=str, default="../scf",
                         metavar="DIR",
                         help="Directory containing EIGVAL.OUT and "
                              "EFERMI.OUT, used to compute VBM - E_F "
                              "(default: ../scf)")
    parser.add_argument("--y", nargs=2, type=float, default=None,
                         metavar=("YMIN", "YMAX"),
                         help="Y-axis limits, e.g. --y -5 5 "
                              "(default: -10 15, or auto with --nres)")
    parser.add_argument("--nres", action="store_true",
                         help="Plot raw (non-referenced) energies instead "
                              "of E - VBM. Elk reports E - E_F in BAND.OUT, "
                              "so the raw energy is recovered as "
                              "(E - E_F) + E_F, using E_F from "
                              "<scf-dir>/EFERMI.OUT. The VBM is not needed "
                              "in this mode, so EIGVAL.OUT is not read.")
    args = parser.parse_args()

    efermi_file = os.path.join(args.scf_dir, "EFERMI.OUT")
    if not os.path.isfile(efermi_file):
        sys.exit(f"Error: {efermi_file} not found.")
    ef_ha = read_fermi_energy(efermi_file)

    k, bands_ha = read_bands(BAND_FILE)

    if args.nres:
        # Raw energies: Elk already wrote E - E_F, so add E_F back.
        #print(f"E_F = {ef_ha:.10f} Ha  ({ef_ha * HA_TO_EV:.6f} eV)  "
        #      f"[from {args.scf_dir}]")
        bands = (bands_ha + ef_ha) * HA_TO_EV
        ref_line_ev = ef_ha * HA_TO_EV  # Fermi level, now away from zero
    else:
        VBM_HA = get_vbm_minus_ef(args.scf_dir)
        #print(f"VBM - E_F = {VBM_HA:.10f} Ha  "
        #      f"({VBM_HA * HA_TO_EV:.6f} eV)  [from {args.scf_dir}]")
        bands = (bands_ha - VBM_HA) * HA_TO_EV
        ref_line_ev = 0.0  # VBM

    xticks = read_high_symmetry_positions(BANDLINES_FILE)
    labels = read_labels_from_elkin(ELK_IN_FILE)

    if len(labels) != len(xticks):
        print(f"Warning: {len(xticks)} high-symmetry points found in "
              f"{BANDLINES_FILE} but {len(labels)} labels parsed from "
              f"{ELK_IN_FILE}. Using numeric tick labels instead.")
        labels = [str(i) for i in range(len(xticks))]

    fig, ax = plt.subplots()#figsize=(8, 6))

    for band in bands:
        ax.plot(k, band, linewidth=1, color='xkcd:blue')

    ax.set_xlim(k.min(), k.max())

    # Fermi / VBM reference line
    ax.axhline(ref_line_ev, linestyle='--', linewidth=0.8, color='xkcd:black')

    # High-symmetry vertical lines and tick labels
    for x in xticks:
        ax.axvline(x, linewidth=0.2, color='xkcd:black')
    ax.set_xticks(xticks)
    ax.set_xticklabels(labels, fontsize=12)

    ax.set_ylabel(r'Energy (eV)', fontsize=14)
    if args.y is not None:
        ax.set_ylim(args.y)
    elif not args.nres:
        ax.set_ylim(-10, 15)  # default range, referenced to VBM
    # else: leave auto-scaled, since raw energies have a very different range

    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    main()
