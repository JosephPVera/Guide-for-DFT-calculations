#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

import re
import glob
import sys
import os
import math

# Find all .out files in the current directory and all subfolders
all_out_files = glob.glob("**/*.out", recursive=True)

# Exclude files like slurm-0001.out, slurm-5768.out, etc. (checked by filename only)
out_files = [f for f in all_out_files if not re.match(r"^slurm-\d+\.out$", os.path.basename(f))]

if not out_files:
    print("No valid .out file found in this folder or subfolders.")
    sys.exit(1)

# Matches lines like: "siesta: E_KS(eV) =           -327.1677"
eks_pattern = re.compile(r"E_KS\(eV\)\s*=\s*(-?\d+\.\d+)")

# Matches lines like: "   Tot   -0.000007   -0.000000    0.000000" 
tot_force_pattern = re.compile(
    r"^\s*Tot\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$"
)

# Matches lines like: "siesta: Pressure (total):         -0.06329923  kBar"
pressure_pattern = re.compile(r"Pressure \(total\)\s*:\s*(-?\d+\.\d+)")

# Matches lines like: "   Max    0.001736" 
max_force_pattern = re.compile(r"^\s*Max\s+(-?\d+\.\d+)\s*$")

results = []
for filename in out_files:
    with open(filename) as f:
        lines = f.readlines()

    eks_values = []
    force_values = []
    max_force_values = []
    pressure_values = []

    for line in lines:
        eks_match = eks_pattern.search(line)
        if eks_match:
            eks_values.append(eks_match.group(1))

        force_match = tot_force_pattern.match(line)
        if force_match:
            fx, fy, fz = (float(x) for x in force_match.groups())
            force_values.append(f"{math.sqrt(fx**2 + fy**2 + fz**2):.6f}")

        max_force_match = max_force_pattern.match(line)
        if max_force_match:
            max_force_values.append(max_force_match.group(1))

        pressure_match = pressure_pattern.search(line)
        if pressure_match:
            pressure_values.append(pressure_match.group(1))

    n_iter = max(len(eks_values), len(force_values), len(max_force_values), len(pressure_values))

    def get(values, i):
        return values[i] if i < len(values) else None

    iterations = []
    for i in range(n_iter):
        iterations.append((
            i + 1,
            get(eks_values, i),
            get(force_values, i),
            get(max_force_values, i),
            get(pressure_values, i),
        ))

    folder = os.path.dirname(filename) if os.path.dirname(filename) else "."
    results.append((folder, filename, iterations))

if all(folder.isdigit() for folder, *_ in results):
    results.sort(key=lambda x: int(x[0]))

header = (
    f"{'Iteration':<10} {'Total energy (eV)':>18} {'Total force (eV/Ang)':>22} "
    f"{'Force Max (eV/Ang)':>20} {'Pressure (kBar)':>18}"
)

for folder, filename, iterations in results:
    print(f"\n{filename}")
    print(header)
    print("-" * len(header))
    for it, energy, force, max_force, pressure in iterations:
        energy_str = energy if energy is not None else "(not found)"
        force_str = force if force is not None else "(not found)"
        max_force_str = max_force if max_force is not None else "(not found)"
        pressure_str = pressure if pressure is not None else "(not found)"
        print(f"{it:<10} {energy_str:>18} {force_str:>22} {max_force_str:>20} {pressure_str:>18}")
