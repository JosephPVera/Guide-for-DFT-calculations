#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Usage:
      python3 elk_dos.py [--pdos] [--x] [--y] [--scf-dir]
      
Plot the DOS (ELK), converting energy from Hartree (Ha) to eV.

VBM - E_F is computed automatically from ../scf/EIGVAL.OUT (VBM) and
../scf/EFERMI.OUT (E_F), so that DOS/PDOS energies can be referenced
to the VBM instead of to E_F. By default ELK prints energies as E - E_F.
See page 52, "bandstr".
"""

import argparse
import glob
import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt

HA_TO_EV = 27.211386245988  # 1 Hartree in eV
OCC_THRESHOLD = 1e-3 

ORBITAL_NAMES = ["s", "p", "d", "f", "g", "h", "i"]  

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

def read_pdos_by_orbital(filename):
    """Read a PDOS_S**_A****.OUT file and group blocks by orbital shell.

    Blocks come in groups of size (2l+1): 1 for s, 3 for p, 5 for d,
    7 for f, etc. Not every file has all shells, so shells are only
    added (in order s, p, d, f, ...) as long as a *complete* group of
    blocks for that shell is present. This way:
      - if only s-blocks exist -> only "s" is returned
      - if s and p-blocks exist -> "s" and "p" are returned
      - if s, p and d-blocks exist -> "s", "p", "d" are returned
      - and so on.
    """
    with open(filename) as fh:
        content = fh.read()
    blocks = [b for b in re.split(r"\n\s*\n", content.strip()) if b.strip()]
    block_data = [np.loadtxt(b.splitlines()) for b in blocks]
    energy_ha = block_data[0][:, 0]

    orbitals = {}
    idx = 0
    l = 0
    while idx < len(block_data):
        n_blocks = 2 * l + 1
        chunk = block_data[idx:idx + n_blocks]
        if len(chunk) < n_blocks:
            break  # incomplete group for this shell, stop here
        name = ORBITAL_NAMES[l] if l < len(ORBITAL_NAMES) else f"l{l}"
        orbitals[name] = sum(b[:, 1] for b in chunk)
        idx += n_blocks
        l += 1

    return energy_ha, orbitals

ORBITAL_COLORS = {
    "s": "xkcd:green",
    "p": "xkcd:blue",
    "d": "xkcd:red",
    "f": "xkcd:orange",
    "g": "xkcd:purple",
    "h": "xkcd:brown",
    "i": "xkcd:pink"
}

def main():
    parser = argparse.ArgumentParser(description="Plot ELK DOS/PDOS (Ha -> eV).")
    parser.add_argument("--pdos", nargs="?", const=True, type=int, default=None,
                         metavar="ATOM",
                         help="Plot PDOS. Plots that atom resolved by orbital (s,p,d,f).")
    parser.add_argument("--x", nargs=2, type=float, default=None,
                         metavar=("XMIN", "XMAX"),
                         help="X-axis limits, e.g. --x 0 1")
    parser.add_argument("--y", nargs=2, type=float, default=None,
                         metavar=("YMIN", "YMAX"),
                         help="Y-axis limits, e.g. --y 0 3")
    parser.add_argument("--scf-dir", type=str, default="../scf",
                         metavar="DIR",
                         help="Directory containing EIGVAL.OUT and "
                              "EFERMI.OUT, used to compute VBM - E_F "
                              "(default: ../scf)")
    args = parser.parse_args()
    atom = args.pdos if isinstance(args.pdos, int) else None

    VBM_HA = get_vbm_minus_ef(args.scf_dir)
    #print(f"VBM - E_F = {VBM_HA:.10f} Ha  "
    #      f"({VBM_HA * HA_TO_EV:.6f} eV)  [from {args.scf_dir}]")

    plt.figure()#figsize=(7, 5))

    if args.pdos is not None:
        files = sorted(glob.glob("PDOS_S*_A*.OUT"))
        if atom is not None:
            files = [f for f in files
                     if int(re.search(r"_A(\d+)\.OUT", f).group(1)) == atom]

        for f in files:
            m = re.search(r"PDOS_S(\d+)_A(\d+)\.OUT", f)
            atom_label = f"S{m.group(1)} A{m.group(2)}" if m else f
            if atom is not None:
                energy_ha, orbitals = read_pdos_by_orbital(f)
                energy_ev = (energy_ha - VBM_HA) * HA_TO_EV
                for orb, dos in orbitals.items():
                    dos_ev = dos / HA_TO_EV
                    plt.plot(energy_ev, dos_ev, color=ORBITAL_COLORS.get(orb, "black"), linewidth=1.3,
                             label=f"{atom_label} ({orb})")
            else:
                data = np.loadtxt(f)
                energy_ha = data[:, 0]
                pdos = data[:, 1:].sum(axis=1)  # sum over all channels
                energy_ev = (energy_ha - VBM_HA) * HA_TO_EV
                pdos_ev = pdos / HA_TO_EV
                plt.plot(energy_ev, pdos_ev, linewidth=1.3, label=atom_label)

        plt.legend(frameon=False)
        plt.ylabel("PDOS (states/eV)", fontsize=14)
        #plt.title("Projected Density of States")
        if atom is not None:
            output_file = f"pdos_plot_{atom}.png"
        else:
            output_file = "pdos_plot.png"
    else:
        data = np.loadtxt("TDOS.OUT")
        energy_ha = data[:, 0]
        dos = data[:, 1]
        energy_ev = (energy_ha - VBM_HA) * HA_TO_EV
        dos_ev = dos / HA_TO_EV

        plt.plot(energy_ev, dos_ev, color="xkcd:blue", linewidth=1.3)
        plt.ylabel("DOS (states/eV)", fontsize=14)
        #plt.title("Density of States", fontsize=14)
        output_file = "dos_plot.png"

    plt.axvline(x=0, color='xkcd:black', linestyle='--', linewidth=0.8)
    plt.xlabel("E - VBM (eV)", fontsize=14)

    if args.x is not None:
        plt.xlim(args.x)
    if args.y is not None:
        plt.ylim(args.y)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)

if __name__ == "__main__":
    main()
