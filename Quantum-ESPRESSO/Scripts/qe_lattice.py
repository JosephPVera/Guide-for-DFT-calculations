#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-07

import re
import glob
import sys
import os

# print the lattice parameters after relaxation calculation

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

# Case 1: neither block found
if cell_idx is None and atomic_idx is None:
    print("No CELL_PARAMETERS or ATOMIC_POSITIONS block found.")
    sys.exit(1)

def get_atomic_block(lines, start_idx):
    end_idx = None
    for i in range(start_idx + 1, len(lines)):
        if "End final coordinates" in lines[i]:
            end_idx = i
            break
    if end_idx is not None:
        return lines[start_idx:end_idx + 1]

    # Fallback: no "End final coordinates" marker found (e.g. not a relax/vc-relax run)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() == "":
            return lines[start_idx:i]
    return lines[start_idx:]


# Case 2: both CELL_PARAMETERS and ATOMIC_POSITIONS exist -> print both
if cell_idx is not None and atomic_idx is not None:
    for line in lines[cell_idx:cell_idx + 4]:
        print(line.rstrip())
    print()
    for line in get_atomic_block(lines, atomic_idx):
        print(line.rstrip())

# Case 3: only ATOMIC_POSITIONS exists -> print only that
elif atomic_idx is not None:
    for line in get_atomic_block(lines, atomic_idx):
        print(line.rstrip())

# Case 4: only CELL_PARAMETERS exists -> print only that
elif cell_idx is not None:
    for line in lines[cell_idx:cell_idx + 4]:
        print(line.rstrip())
