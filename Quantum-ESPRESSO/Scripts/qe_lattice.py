#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-07

import re
import glob
import sys
import os

# print the lattice parameters

# Find all .out files in the current directory (adjust if you want recursive search)
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

# Find the index of the LAST line starting with CELL_PARAMETERS
cell_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith("CELL_PARAMETERS"):
        cell_idx = i

# Find the index of the LAST line starting with ATOMIC_POSITIONS
atomic_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith("ATOMIC_POSITIONS"):
        atomic_idx = i

# Print CELL_PARAMETERS block
if cell_idx is not None:
    #print("=== CELL_PARAMETERS (last occurrence) ===")
    for line in lines[cell_idx:cell_idx + 4]:
        print(line.rstrip())
else:
    print("No CELL_PARAMETERS line found.")

print()

# Print ATOMIC_POSITIONS block
if atomic_idx is not None:
    #print("=== ATOMIC_POSITIONS (last occurrence) ===")
    for line in lines[atomic_idx:atomic_idx + 4]:
        print(line.rstrip())
else:
    print("No ATOMIC_POSITIONS line found.")
