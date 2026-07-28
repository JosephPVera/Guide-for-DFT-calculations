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

vbm = None
cbm = None

for line in lines:
    match = re.search(
        r"highest occupied, lowest unoccupied level\s*\(ev\):\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)",
        line
    )
    if match:
        vbm = match.group(1)
        cbm = match.group(2)

if vbm is not None and cbm is not None:
    # Determine number of decimals from the VBM string to keep consistent precision
    decimals = len(vbm.split(".")[1])
    gap = round(float(cbm) - float(vbm), decimals)

    print(f"{'VBM (eV)':<14} {'CBM (eV)':<15} {'Gap (eV)':<15}")
    print("-" * 40)
    print(f"{vbm:<14} {cbm:<15} {gap:<15.{decimals}f}")
else:
    print("No 'highest occupied, lowest unoccupied level' line found.")
