#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Extract, for every folder containing a Quantum ESPRESSO run:
    - folder name
    - lattice constant --> celldm(1) / A, in the units given in the .in file, or computed from CELL_PARAMETERS
    - cell volume --> computed from CELL_PARAMETERS, or from celldm's for common ibrav values if no CELL_PARAMETERS card is present
    - total energy --> from the .out file
"""

import re
import glob
import sys
import os

BOHR_TO_ANG = 0.529177210903

def parse_in_file(filename):
    """Return (lattice_constant, volume) from a QE .in file."""
    with open(filename) as f:
        text = f.read()

    # --- ibrav ---
    ibrav = None
    m = re.search(r"ibrav\s*=\s*(-?\d+)", text)
    if m:
        ibrav = int(m.group(1))

    # --- celldm's ---
    celldm = {}
    for m in re.finditer(r"celldm\((\d)\)\s*=\s*([-\d.eEdD]+)", text):
        idx = int(m.group(1))
        val = float(m.group(2).replace("d", "e").replace("D", "E"))
        celldm[idx] = val

    # --- A, B, C, cosAB, cosAC, cosBC (alternative to celldm) ---
    A = None
    m = re.search(r"(?<![A-Za-z_])A\s*=\s*([-\d.eEdD]+)", text)
    if m:
        A = float(m.group(1).replace("d", "e").replace("D", "E"))

    # Lattice constant to report: prefer celldm(1) [bohr], else A [Angstrom]
    lattice_const = None
    lattice_unit = None
    if 1 in celldm:
        lattice_const = celldm[1]
        lattice_unit = "bohr"
    elif A is not None:
        lattice_const = A
        lattice_unit = "Ang"

    # --- CELL_PARAMETERS block (if present) ---
    volume = None
    volume_unit = None
    m = re.search(
        r"CELL_PARAMETERS\s*(?:\{|\()?\s*(\w+)?\s*(?:\}|\))?\s*\n"
        r"\s*([-\d.eEdD]+)\s+([-\d.eEdD]+)\s+([-\d.eEdD]+)\s*\n"
        r"\s*([-\d.eEdD]+)\s+([-\d.eEdD]+)\s+([-\d.eEdD]+)\s*\n"
        r"\s*([-\d.eEdD]+)\s+([-\d.eEdD]+)\s+([-\d.eEdD]+)",
        text,
    )
    if m:
        unit = (m.group(1) or "alat").lower()
        nums = [float(g.replace("d", "e").replace("D", "E")) for g in m.groups()[1:]]
        v1 = nums[0:3]
        v2 = nums[3:6]
        v3 = nums[6:9]

        def det3(a, b, c):
            return (
                a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])
            )

        # compute lattice parameter from CELL_PARAMETERS. if it was not declared through celldm(1) or A.
        if lattice_const is None:
            def vector_length(v):
                return (v[0]**2 + v[1]**2 + v[2]**2)**0.5

            if "angstrom" in unit:
                lattice_const = vector_length(v1)
                lattice_unit = "Ang"

            elif "bohr" in unit:
                lattice_const = vector_length(v1)
                lattice_unit = "bohr"

        vol_raw = abs(det3(v1, v2, v3))

        if "alat" in unit or unit == "":
            # vectors are in units of celldm(1) (or A)
            if lattice_unit == "bohr" and lattice_const is not None:
                volume = vol_raw * lattice_const**3
                volume_unit = "bohr^3"
            elif lattice_unit == "Ang" and lattice_const is not None:
                volume = vol_raw * lattice_const**3
                volume_unit = "Ang^3"
        elif "bohr" in unit:
            volume = vol_raw
            volume_unit = "bohr^3"
        elif "angstrom" in unit:
            volume = vol_raw
            volume_unit = "Ang^3"

    if volume is None and ibrav is not None and 1 in celldm:
        a = celldm[1]
        if ibrav == 1:  # simple cubic
            volume = a**3
            volume_unit = "bohr^3"
        elif ibrav == 2:  # fcc
            volume = 0.25 * a**3
            volume_unit = "bohr^3"
        elif ibrav == 3:  # bcc
            volume = 0.5 * a**3
            volume_unit = "bohr^3"
        elif ibrav == 4 and 3 in celldm:  # hexagonal (e.g. graphene)
            c_over_a = celldm[3]
            volume = (3**0.5 / 2.0) * a**2 * (c_over_a * a)
            volume_unit = "bohr^3"

    return lattice_const, lattice_unit, volume, volume_unit

def parse_out_file(filename):
    with open(filename) as f:
        lines = f.readlines()

    last_energy_single = None
    last_energy_double = None
    for line in lines:
        if re.match(r"^\s*!!\s*total energy\s*=", line):
            match = re.search(r"total energy\s*=\s*(-?\d+\.\d+)\s*(\w+)", line)
            if match:
                last_energy_double = match.group(1)
        elif re.match(r"^\s*!\s*total energy\s*=", line):
            match = re.search(r"total energy\s*=\s*(-?\d+\.\d+)\s*(\w+)", line)
            if match:
                last_energy_single = match.group(1)

    return last_energy_double if last_energy_double is not None else last_energy_single

all_in_files = glob.glob(os.path.join(".", "**", "*.in"), recursive=True)
all_out_files = glob.glob(os.path.join(".", "**", "*.out"), recursive=True)
out_files = [f for f in all_out_files if not re.match(r"^slurm-\d+\.out$", os.path.basename(f))]

if not all_in_files:
    print("No .in file found in this folder or subfolders.")
    sys.exit(1)
if not out_files:
    print("No valid .out file found in this folder or subfolders.")
    sys.exit(1)

out_by_folder = {}
for f in out_files:
    folder = os.path.dirname(f) if os.path.dirname(f) else "."
    out_by_folder.setdefault(folder, f)

results = []
for in_file in all_in_files:
    folder_path = os.path.dirname(in_file) if os.path.dirname(in_file) else "."
    folder_name = os.path.basename(os.path.normpath(folder_path))
    lattice_const, lattice_unit, volume, volume_unit = parse_in_file(in_file)

    out_file = out_by_folder.get(folder_path)
    energy = parse_out_file(out_file) if out_file else None

    results.append((folder_name, lattice_const, lattice_unit, volume, volume_unit, energy))

if all(r[0].isdigit() for r in results):
    results.sort(key=lambda r: int(r[0]))
else:
    results.sort(key=lambda r: r[0])

# --- print table ---
header = f"{'# folder':<8} {'lattice':>15} {'volumen':>18} {'total energy (Ry)':>20}"
print(header)

with open("results.dat", "w") as output:
    output.write(header + "\n")

    for folder, lat, lat_u, vol, vol_u, energy in results:
        lat_str = f"{lat:.6f}" if lat is not None else "(not found)"
        vol_str = f"{vol:.6f}" if vol is not None else "(not found)"
        e_str = energy if energy is not None else "(not found)"

        line = f"{folder:<8} {lat_str:>15} {vol_str:>18} {e_str:>20}"

        print(line)
        output.write(line + "\n")
