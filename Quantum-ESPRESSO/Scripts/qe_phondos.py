#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Usage:
    qe_phondos.py [--pdos] [--x 1 12] [--y 0 50]     # [plots only pdos1, pdos2, ...]
    qe_phondos.py --x 1 12     # for example: set x-axis range from 1 to 12
    qe_phondos.py --y 0 50     # for example: set y-axis range from 0 to 50
"""
import argparse
import glob
import sys
import numpy as np
import matplotlib.pyplot as plt

CM1_TO_THZ = 0.0299792458  # 1 cm^-1 = 0.0299792458 THz

def find_dos_file():
    matches = sorted(glob.glob("*.dos"))
    if not matches:
        sys.exit("Error: no .dos file found in the current directory.")
    if len(matches) > 1:
        print(f"Warning: multiple .dos files found {matches}, using '{matches[0]}'.")
    return matches[0]
    
def parse_args():
    p = argparse.ArgumentParser(description="Plot DOS or PDOS from a .dos file")
    p.add_argument("--pdos", action="store_true",
                    help="plot only the PDOS columns (pdos1, pdos2, ...) instead of the total DOS")
    p.add_argument("-o", "--output", default=None,
                    help="output image filename (default: <file_stem>_dos.png or _pdos.png)")
    p.add_argument("--x", nargs=2, type=float, metavar=("XMIN", "XMAX"), default=None,
                    help="set x-axis range, e.g. --x 1 12")
    p.add_argument("--y", nargs=2, type=float, metavar=("YMIN", "YMAX"), default=None,
                    help="set y-axis range, e.g. --y 0 50")
    return p.parse_args()
    
def main():
    args = parse_args()
    dos_file = find_dos_file()
    print(f"File found: {dos_file}")
    
    data = np.loadtxt(dos_file)
    
    freq = data[:, 0] * CM1_TO_THZ    # cm^-1 -> THz
    dos = data[:, 1] * (1 / CM1_TO_THZ)
    pdos_cols = data[:, 2:] * (1 / CM1_TO_THZ)  # 0, 1, 2, ... pdos columns (may be empty)
    n_pdos = pdos_cols.shape[1]
    
    fig, ax = plt.subplots()
    
    if args.pdos:
        if n_pdos == 0:
            sys.exit(f"Error: --pdos requested but '{dos_file}' has no PDOS columns.")
        colors = ['xkcd:red', 'xkcd:green', 'xkcd:yellow', 'xkcd:brown', 'xkcd:cyan'] #plt.cm.tab10(np.linspace(0, 1, n_pdos))
        for i in range(n_pdos):
            ax.plot(freq, pdos_cols[:, i], lw=1, color=colors[i], label=f"pdos{i+1}")
        ymax = pdos_cols.max()
        default_suffix = "_pdos.png"
    else:
        ax.plot(freq, dos, c='xkcd:blue', lw=1, label='Total')
        ymax = dos.max()
        default_suffix = "_dos.png"
        
    ax.set_xlabel(r'Frecuency (THz)')
    ax.set_ylabel(r'DOS (state/THz/u.c.)')
    ax.legend(frameon=False, loc='upper left')
    
    if args.x is not None:
        ax.set_xlim(args.x[0], args.x[1])
    else:
        ax.set_xlim(freq[0], freq[-1])
        
    if args.y is not None:
        ax.set_ylim(args.y[0], args.y[1])
    else:
        ax.set_ylim(0, ymax * 1.1)
        
    fig.tight_layout()
    
    stem = dos_file.rsplit(".", 1)[0]
    outname = args.output or f"{stem}{default_suffix}"
    fig.savefig(outname, dpi=150)
    #print(f"Saved: {outname}")
    
if __name__ == "__main__":
    main()
