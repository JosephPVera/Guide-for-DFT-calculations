#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Compute VBM, CBM, and band gap from an EIGVAL.OUT file (Elk format).

The script always reads a file named EIGVAL.OUT in the current directory
and prints a small table:

    Row 1: VBM, CBM, Gap in Hartree (Ha)   -- native units of EIGVAL.OUT
    Row 2: VBM, CBM, Gap in eV
"""

import math
import re
import sys

HARTREE_TO_EV = 27.211386245988
OCC_THRESHOLD = 1e-3  # occupancy above this is considered "occupied"
FILENAME = "EIGVAL.OUT"
SIG_FIGS = 11  # significant digits used for eigenvalues in EIGVAL.OUT

def fmt_sigfigs(value, sig_figs=SIG_FIGS):
    """Format value in fixed-point notation with `sig_figs` significant
    digits, matching the precision convention used in EIGVAL.OUT (where
    the number of decimal places shrinks as the integer part grows)."""
    if value == 0:
        decimals = sig_figs - 1
    else:
        integer_digits = max(1, math.floor(math.log10(abs(value))) + 1)
        decimals = max(0, sig_figs - integer_digits)
    return f"{value:.{decimals}f}"

def parse_eigval(filename):
    """Parse EIGVAL.OUT and return list of (eigenvalue, occupancy) tuples."""
    states = []
    line_re = re.compile(
        r"^\s*\d+\s+([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s+"
        r"([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s*$"
    )

    with open(filename, "r") as f:
        for line in f:
            m = line_re.match(line)
            if m:
                eigenvalue = float(m.group(1))
                occupancy = float(m.group(2))
                states.append((eigenvalue, occupancy))

    return states

def compute_vbm_cbm_gap(states):
    occupied = [e for e, occ in states if occ > OCC_THRESHOLD]
    unoccupied = [e for e, occ in states if occ <= OCC_THRESHOLD]

    if not occupied:
        sys.exit("Error: no occupied states found (check OCC_THRESHOLD).")
    if not unoccupied:
        sys.exit("Error: no unoccupied states found (check OCC_THRESHOLD).")

    vbm = max(occupied)
    cbm = min(unoccupied)
    gap = cbm - vbm
    return vbm, cbm, gap

def main():
    states = parse_eigval(FILENAME)
    if not states:
        sys.exit(f"Error: no eigenvalue/occupancy data found in {FILENAME}.")

    vbm_ha, cbm_ha, gap_ha = compute_vbm_cbm_gap(states)
    vbm_ev = vbm_ha * HARTREE_TO_EV
    cbm_ev = cbm_ha * HARTREE_TO_EV
    gap_ev = gap_ha * HARTREE_TO_EV

    header = f"{'VBM':>18} {'CBM':>18} {'Gap':>18}"
    print(header)
    print(f"{fmt_sigfigs(vbm_ha):>18} {fmt_sigfigs(cbm_ha):>18} {fmt_sigfigs(gap_ha):>18}   (Ha)")
    print(f"{fmt_sigfigs(vbm_ev):>18} {fmt_sigfigs(cbm_ev):>18} {fmt_sigfigs(gap_ev):>18}   (eV)")

if __name__ == "__main__":
    main()
