#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

import re
import glob
import sys
import os

# Find all .out files in the current directory and all subfolders
all_out_files = glob.glob("**/*.out", recursive=True)

# Exclude files like slurm-0001.out, slurm-5768.out, etc. (checked by filename only)
out_files = [f for f in all_out_files if not re.match(r"^slurm-\d+\.out$", os.path.basename(f))]

if not out_files:
    print("No valid .out file found in this folder or subfolders.")
    sys.exit(1)

results = []

for filename in out_files:
    with open(filename) as f:
        lines = f.readlines()

    last_energy = None
    for line in lines:
        if re.match(r"^\s*!\s*total energy\s*=", line):
            match = re.search(r"total energy\s*=\s*(-?\d+\.\d+)\s*(\w+)", line)
            if match:
                last_energy = match.group(1)

    folder = os.path.dirname(filename) if os.path.dirname(filename) else "."
    results.append((folder, last_energy))

# If ALL folder names are numeric, sort ascending by numeric value
if all(folder.isdigit() for folder, _ in results):
    results.sort(key=lambda x: int(x[0]))

# Print as a table
print(f"{'Folder':<5} {'Total energy (Ry)':>20}")
print("-" * 28)
for folder, energy in results:
    if energy is not None:
        print(f"{folder:<5} {energy:>20}")
    else:
        print(f"{folder:<5} {'(not found)':>20}")
