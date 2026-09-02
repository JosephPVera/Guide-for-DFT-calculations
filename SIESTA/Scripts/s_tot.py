#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

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

# Matches lines like: "siesta: E_KS(eV) =           -327.1677"
eks_pattern = re.compile(r"E_KS\(eV\)\s*=\s*(-?\d+\.\d+)")

results = []
for filename in out_files:
    with open(filename) as f:
        lines = f.readlines()

    last_eks = None
    for line in lines:
        match = eks_pattern.search(line)
        if match:
            last_eks = match.group(1)

    folder = os.path.dirname(filename) if os.path.dirname(filename) else "."
    results.append((folder, last_eks))

if all(folder.isdigit() for folder, _ in results):
    results.sort(key=lambda x: int(x[0]))

print(f"{'Folder':<5} {'Total energy (eV)':>20}")
print("-" * 28)
for folder, energy in results:
    if energy is not None:
        print(f"{folder:<5} {energy:>20}")
    else:
        print(f"{folder:<5} {'(not found)':>20}")
