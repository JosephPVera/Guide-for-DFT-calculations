#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

"""
Find the VBM (Valence Band Maximum), CBM (Conduction Band Minimum), and
the resulting band gap (direct or indirect) from an occupancy.dat file
produced by s_occupations.py.
"""

import sys

def count_decimals(number_str):
    """Number of digits after the decimal point in a numeric string."""
    return len(number_str.split(".")[1]) if "." in number_str else 0

def parse_occupancy(path):
    """Parse an occupancy.dat file"""
    e_fermi = None
    e_fermi_decimals = None
    eig_decimals = None
    occ_decimals = None
    records = []

    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                if "fermi energy" in stripped.lower():
                    value_str = stripped.split(":")[-1].strip()
                    try:
                        e_fermi = float(value_str)
                        e_fermi_decimals = count_decimals(value_str)
                    except ValueError:
                        pass
                continue

            tokens = stripped.split()
            if len(tokens) != 5:
                continue  # skip anything that doesn't look like a data row

            kidx, spin, band, eig, occ = tokens
            if eig_decimals is None:
                eig_decimals = count_decimals(eig)
                occ_decimals = count_decimals(occ)

            records.append({
                "kidx": int(kidx),
                "spin": int(spin),
                "band": int(band),
                "eig": float(eig),
                "occ": float(occ),
            })

    if not records:
        sys.exit(f"Error: no data rows found in {path}.")

    return e_fermi, e_fermi_decimals, eig_decimals, occ_decimals, records

def compute_band_gap(records):
    """Find VBM, CBM, gap, and its direct/indirect character.

    A state is "occupied" if its occupation is above half of the maximum
    occupation found in the data (adapts automatically to spin degeneracy:
    1.0 for non-polarized states with max occupation 2.0, 0.5 for
    polarized/non-collinear/spin-orbit states with max occupation 1.0).
    """
    max_occ = max(r["occ"] for r in records)
    threshold = max_occ / 2.0

    occupied = [r for r in records if r["occ"] > threshold]
    unoccupied = [r for r in records if r["occ"] <= threshold]

    if not occupied or not unoccupied:
        sys.exit(
            "Error: could not find both occupied and unoccupied states "
            "in occupancy.dat."
        )

    vbm_rec = max(occupied, key=lambda r: r["eig"])
    cbm_rec = min(unoccupied, key=lambda r: r["eig"])
    band_gap = cbm_rec["eig"] - vbm_rec["eig"]
    is_direct = (vbm_rec["kidx"] == cbm_rec["kidx"])

    per_kpt_direct_gap = {}
    for kidx in {r["kidx"] for r in records}:
        occ_here = [r["eig"] for r in occupied if r["kidx"] == kidx]
        unocc_here = [r["eig"] for r in unoccupied if r["kidx"] == kidx]
        if occ_here and unocc_here:
            per_kpt_direct_gap[kidx] = min(unocc_here) - max(occ_here)

    min_direct_gap = None
    min_direct_gap_kpt = None
    if per_kpt_direct_gap:
        min_direct_gap_kpt = min(per_kpt_direct_gap,
                                  key=per_kpt_direct_gap.get)
        min_direct_gap = per_kpt_direct_gap[min_direct_gap_kpt]

    return {
        "threshold": threshold,
        "vbm": vbm_rec["eig"],
        "vbm_kpt": vbm_rec["kidx"],
        "vbm_spin": vbm_rec["spin"],
        "cbm": cbm_rec["eig"],
        "cbm_kpt": cbm_rec["kidx"],
        "cbm_spin": cbm_rec["spin"],
        "band_gap": band_gap,
        "is_direct": is_direct,
        "min_direct_gap": min_direct_gap,
        "min_direct_gap_kpt": min_direct_gap_kpt,
    }

def main():
    occ_path = "occupancy.dat"
    print(f"Reading occupations from: {occ_path}\n")

    e_fermi, e_fermi_dec, eig_dec, occ_dec, records = parse_occupancy(occ_path)

    nband = max(r["band"] for r in records)
    nkpt = len({r["kidx"] for r in records})
    nspin = len({r["spin"] for r in records})

    if e_fermi is not None:
        dec = e_fermi_dec if e_fermi_dec is not None else eig_dec

    result = compute_band_gap(records)

    print(f"VBM (Valence Band Maximum)    : "
          f"{result['vbm']:.{eig_dec}f} eV  "
          f"at k-point {result['vbm_kpt']}, spin {result['vbm_spin']}")
    print(f"CBM (Conduction Band Minimum) : "
          f"{result['cbm']:.{eig_dec}f} eV  "
          f"at k-point {result['cbm_kpt']}, spin {result['cbm_spin']}")
    print(f"Band gap (CBM - VBM)          : "
          f"{result['band_gap']:.{eig_dec}f} eV")
    print()

    if result["band_gap"] <= 0:
        print("-> The occupied and unoccupied states overlap in energy: "
              "the system appears to be metallic (no gap).")
        return

    if result["is_direct"]:
        print(f"-> Gap character: DIRECT (VBM and CBM at the same "
              f"k-point: {result['vbm_kpt']})")
    else:
        print(f"-> Gap character: INDIRECT "
              f"(VBM at k-point {result['vbm_kpt']}, "
              f"CBM at k-point {result['cbm_kpt']})")
        if result["min_direct_gap"] is not None:
            print(f"   Smallest direct gap (same k-point) = "
                  f"{result['min_direct_gap']:.{eig_dec}f} eV, "
                  f"found at k-point {result['min_direct_gap_kpt']}")

if __name__ == "__main__":
    main()
