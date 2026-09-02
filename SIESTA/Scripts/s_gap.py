#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Finds VBM, CBM and the band gap from a *.EIG eigenvalue file.

Physical idea
-------------
The Fermi energy (first line of the .EIG file) separates occupied
states (below or at E_fermi) from unoccupied states (above E_fermi).
So:
    VBM (Valence Band Maximum)    = highest eigenvalue with E <= E_fermi
    CBM (Conduction Band Minimum) = lowest  eigenvalue with E >  E_fermi
    Band gap = CBM - VBM

The script also reports whether the gap is direct (VBM and CBM occur
at the same k-point) or indirect, and prints the direct gap at every
k-point for reference.
"""

import sys
import re
import glob
import os

def find_eig_file(explicit_path=None):
    """Return the path to the .EIG file to use."""
    if explicit_path:
        if not os.path.isfile(explicit_path):
            sys.exit(f"Error: file not found: {explicit_path}")
        return explicit_path

    candidates = sorted(glob.glob("*.EIG")) + sorted(glob.glob("*.eig"))
    if not candidates:
        sys.exit(
            "Error: no .EIG file found in the current directory. "
            "Pass the path explicitly: s_gap.py file.EIG"
        )
    if len(candidates) > 1:
        print(f"Note: multiple .EIG files found, using '{candidates[0]}'. "
              f"Others: {candidates[1:]}")
    return candidates[0]

_FORTRAN_FLOAT_RE = re.compile(
    r'^([+-]?)(\d*)\.(\d+)(?:[eEdD]([+-]?\d+))?$'
)

def parse_fortran_float(token):
    """Parse a numeric token and figure out how many decimal digits it
    needs when printed in plain (non-exponential) notation, so that the
    same number of significant figures as in the source file is kept.

    E.g. '-0.193658753E+02' -> (-19.3658753, 7)
         '-0.193658753E+01' -> (-1.93658753, 8)
    """
    token = token.strip()
    value = float(token)

    match = _FORTRAN_FLOAT_RE.match(token)
    if not match:
        return value, 6

    _, _, frac_digits, exponent = match.groups()
    exponent = int(exponent) if exponent else 0

    ndec = len(frac_digits) - exponent
    if ndec < 0:
        ndec = 0

    return value, ndec

def parse_eig(path):
    with open(path, "r") as f:
        tokens_by_line = [line.split() for line in f if line.strip()]

    if len(tokens_by_line) < 2:
        sys.exit("Error: .EIG file is too short / malformed.")

    # Line 1: Fermi energy
    e_fermi, e_fermi_ndec = parse_fortran_float(tokens_by_line[0][0])

    # Line 2: nband nsppol nkpt
    header = tokens_by_line[1]
    nband, nsppol, nkpt = int(header[0]), int(header[1]), int(header[2])

    eigenvalues = {}
    current_kpt = None
    current_values = []

    for tokens in tokens_by_line[2:]:
        is_new_block = (
            current_kpt is None or len(current_values) >= nband
        )

        if is_new_block:
            if current_kpt is not None and current_values:
                eigenvalues[current_kpt] = current_values

            current_kpt = int(tokens[0])
            current_values = [parse_fortran_float(x) for x in tokens[1:]]
        else:
            current_values.extend(parse_fortran_float(x) for x in tokens)

    if current_kpt is not None and current_values:
        eigenvalues[current_kpt] = current_values

    for kpt, values in eigenvalues.items():
        if len(values) != nband:
            print(
                f"Warning: k-point {kpt} has {len(values)} eigenvalues, "
                f"expected {nband}."
            )

    if len(eigenvalues) != nkpt:
        print(
            f"Warning: found {len(eigenvalues)} k-points, "
            f"header declared {nkpt}."
        )

    return e_fermi, e_fermi_ndec, nband, nkpt, eigenvalues

def compute_band_gap(e_fermi, eigenvalues):
    """Compute VBM, CBM and band gap using the Fermi energy as the
    boundary between occupied and unoccupied states."""

    vbm = -float("inf")
    vbm_ndec = 0
    vbm_kpt = None
    cbm = float("inf")
    cbm_ndec = 0
    cbm_kpt = None

    per_kpt_direct_gap = {}

    for kpt, values in eigenvalues.items():
        occupied = [(v, n) for v, n in values if v <= e_fermi]
        unoccupied = [(v, n) for v, n in values if v > e_fermi]

        local_vbm = local_cbm = None

        if occupied:
            local_vbm, local_vbm_ndec = max(occupied, key=lambda t: t[0])
            if local_vbm > vbm:
                vbm = local_vbm
                vbm_ndec = local_vbm_ndec
                vbm_kpt = kpt

        if unoccupied:
            local_cbm, local_cbm_ndec = min(unoccupied, key=lambda t: t[0])
            if local_cbm < cbm:
                cbm = local_cbm
                cbm_ndec = local_cbm_ndec
                cbm_kpt = kpt

        if local_vbm is not None and local_cbm is not None:
            gap_ndec = max(local_vbm_ndec, local_cbm_ndec)
            per_kpt_direct_gap[kpt] = (local_cbm - local_vbm, gap_ndec)

    if vbm_kpt is None or cbm_kpt is None:
        sys.exit(
            "Error: could not find both occupied and unoccupied states "
            "around the Fermi energy. Check the input file."
        )

    band_gap = cbm - vbm
    band_gap_ndec = max(vbm_ndec, cbm_ndec)
    is_direct = (vbm_kpt == cbm_kpt)

    min_direct_gap, min_direct_gap_ndec = min(
        per_kpt_direct_gap.values(), key=lambda t: t[0]
    )
    min_direct_gap_kpt = min(
        per_kpt_direct_gap, key=lambda k: per_kpt_direct_gap[k][0]
    )

    return {
        "vbm": vbm,
        "vbm_ndec": vbm_ndec,
        "vbm_kpt": vbm_kpt,
        "cbm": cbm,
        "cbm_ndec": cbm_ndec,
        "cbm_kpt": cbm_kpt,
        "band_gap": band_gap,
        "band_gap_ndec": band_gap_ndec,
        "is_direct": is_direct,
        "min_direct_gap": min_direct_gap,
        "min_direct_gap_ndec": min_direct_gap_ndec,
        "min_direct_gap_kpt": min_direct_gap_kpt,
    }

def main():
    explicit_path = sys.argv[1] if len(sys.argv) > 1 else None
    eig_path = find_eig_file(explicit_path)

    print(f"Reading eigenvalues from: {eig_path}\n")

    e_fermi, e_fermi_ndec, nband, nkpt, eigenvalues = parse_eig(eig_path)

    result = compute_band_gap(e_fermi, eigenvalues)

    print(f"VBM (Valence Band Maximum)    : "
          f"{result['vbm']:.{result['vbm_ndec']}f}  "
          f"at k-point {result['vbm_kpt']}")
    print(f"CBM (Conduction Band Minimum) : "
          f"{result['cbm']:.{result['cbm_ndec']}f}  "
          f"at k-point {result['cbm_kpt']}")
    print(f"Band gap (CBM - VBM)          : "
          f"{result['band_gap']:.{result['band_gap_ndec']}f}")
    print()

    if result["is_direct"]:
        print(f"-> Gap character: DIRECT (VBM and CBM at the same "
              f"k-point: {result['vbm_kpt']})")
    else:
        print(f"-> Gap character: INDIRECT "
              f"(VBM at k-point {result['vbm_kpt']}, "
              f"CBM at k-point {result['cbm_kpt']})")
        print(f"   Smallest direct gap (same k-point) = "
              f"{result['min_direct_gap']:.{result['min_direct_gap_ndec']}f}, "
              f"found at k-point {result['min_direct_gap_kpt']}")

if __name__ == "__main__":
    main()
