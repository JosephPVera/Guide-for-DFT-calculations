#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-07

import re
import glob
import sys
import os

# Find all .out files in the current directory
all_out_files = glob.glob("*.out")

out_files = [f for f in all_out_files if not re.match(r"^slurm-\d+\.out$", os.path.basename(f))]

if not out_files:
    print("No valid .out file found in this folder.")
    sys.exit(1)
elif len(out_files) > 1:
    print(f"Multiple .out files found: {out_files}")
    print(f"Using the first one: {out_files[0]}")

filename = out_files[0]
print(f"Reading: {filename}\n")

with open(filename) as f:
    lines = f.readlines()

energies_single = []  # lines with exactly "!"
energies_double = []  # lines with "!!"
forces = []
pressures = []

for line in lines:
    # "!!   total energy" (double exclamation)
    if re.match(r"^\s*!!\s*total energy\s*=", line):
        match = re.search(r"total energy\s*=\s*(-?\d+\.\d+)", line)
        if match:
            energies_double.append(match.group(1))

    # "!    total energy" (single exclamation, NOT followed by another "!")
    elif re.match(r"^\s*!\s*total energy\s*=", line):
        match = re.search(r"total energy\s*=\s*(-?\d+\.\d+)", line)
        if match:
            energies_single.append(match.group(1))

    # Total force
    if re.match(r"^\s*Total force\s*=", line):
        match = re.search(r"Total force\s*=\s*(-?\d+\.\d+)", line)
        if match:
            forces.append(match.group(1))

    # Pressure (from the "total   stress" line, P= value)
    if "total" in line and "stress" in line and "P=" in line:
        match = re.search(r"P=\s*(-?\d+\.\d+)", line)
        if match:
            pressures.append(match.group(1))

# Prefer "!!" energies if they exist; otherwise fall back to "!" energies
energies = energies_double if energies_double else energies_single

# Pair them up by order (assumes same number of entries)
n = min(len(energies), len(forces), len(pressures))

print(f"{'Iteration':<12} {'Total force (Ry/au)':>15} {'Total energy (Ry)':>18} {'Pressure (kbar)':>16}")
print("-" * 68)
for i in range(n):
    print(f"{i+1:<12} {forces[i]:>19} {energies[i]:>18} {pressures[i]:>16}")

#if not (len(energies) == len(forces) == len(pressures)):
#    print(f"\nWarning: found {len(energies)} energy, {len(forces)} force, {len(pressures)} pressure value(s) — showing only the first {n} matched set(s).")
