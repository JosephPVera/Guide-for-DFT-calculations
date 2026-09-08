#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-09

"""
Usage: 
      python3 formation_energy.py [--all] [--nc] [--qe]
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Defect formation energy plot")
parser.add_argument("--all", action="store_true",
                     help="Plot the minimum curve and all individual charge-state curves. "
                          "By default, only the minimum curve is plotted.")
parser.add_argument("--nc", action="store_true",
                     help="Do not apply finite-size corrections (E_corr). "
                          "By default, corrections are applied.")
parser.add_argument("--qe", action="store_true",
                     help="Interpret E_bulk, E_def, u_C and u_N as Quantum ESPRESSO "
                          "total energies given in Ry, and convert them to eV. "
                          "By default, all input energies are assumed to already be in eV (VASP).")
args = parser.parse_args()

RY_TO_EV = 13.605693122994

# Band edges
E_VBM = 9.646  # VASP
E_CBM = 13.8025 # VASP

Gap = E_CBM - E_VBM

# Fermi energy range
E_F = np.linspace(0, Gap, 500)

# Total energy for perfect supercell (VASP ---> eV, and QE ---> Ry)
E_bulk = -1961.920072 # VASP

# Total energies for defect supercell (VASP ---> eV, and QE ---> Ry), energy corrections, and charge states
E_def = np.array([-1909.157681, -1922.190560, -1934.987194, -1946.164795, -1957.028853, -1966.921169]) # VASP
E_corr = np.array([2.785574281694399, 1.3239220120693769, 0.3797874083283934, 0.0, 0.15225000859821225, 0.7558700990885153]) # VASP

q = np.array([-3, -2, -1, 0, 1, 2])

# Chemical potentials (VASP ---> eV, and QE ---> Ry)
u_C = -9.09304 # VASP
u_N = -8.320881 # VASP

n_C = -2
n_N = 1

u = n_C * u_C + n_N * u_N

# Convert only the QE total energies (E_bulk, E_def, u_C, u_N) from Ry to eV when --qe is set
if args.qe:
    E_bulk = E_bulk * RY_TO_EV
    E_def = E_def * RY_TO_EV

# Corrections are applied by default, --nc disables them
if args.nc:
    E_corr_used = np.zeros_like(E_corr)
else:
    E_corr_used = E_corr
    
if args.qe:
    u = u * RY_TO_EV

# Formation energy is linear in E_F for every charge state: E_form_i(E_F) = a_i * E_F + b_i
a = q.astype(float)
b = (E_def - E_bulk - u + q * E_VBM + E_corr_used)

E_form_all = np.array([a[i] * E_F + b[i] for i in range(len(q))])

# Minimum curve
E_min = np.min(E_form_all, axis=0)
q_min_idx = np.argmin(E_form_all, axis=0) 

# Find the exact intersection points where the dominant charge state switches 
# Two lines a_i*x+b_i and a_j*x+b_j intersect at x = (b_j - b_i) / (a_i - a_j)
intersections = []
for k in range(len(q_min_idx) - 1):
    i, j = q_min_idx[k], q_min_idx[k + 1]
    if i != j:
        if a[i] == a[j]:
            continue  
        x_cross = (b[j] - b[i]) / (a[i] - a[j])
        # Keep only crossings within the plotted Fermi-level range
        if E_F[0] <= x_cross <= E_F[-1]:
            y_cross = a[i] * x_cross + b[i]
            intersections.append((x_cross, y_cross, q[i], q[j]))

# Remove near-duplicate points (in case a crossing lands exactly on a grid node)
unique_intersections = []
for pt in intersections:
    if not any(np.isclose(pt[0], u[0], atol=1e-6) for u in unique_intersections):
        unique_intersections.append(pt)

plt.figure()

if args.all:
    for i, charge in enumerate(q):
        plt.plot(E_F, E_form_all[i], linewidth=1, alpha=0.4, label=f"q={charge:+d}")

# Minimum curve
plt.plot(E_F, E_min, color="black", linewidth=2)#, label="Minimum curve")

# Mark the intersection (charge-transition) points
for x_cross, y_cross, qi, qj in unique_intersections:
    plt.plot(x_cross, y_cross, "o", color="red", markersize=7, zorder=5)

plt.axvline(Gap, linestyle="-", color="black", linewidth=0.8)
plt.axvline(0, color="black", linewidth=0.8)

plt.xlabel("Fermi level (eV)", fontsize=14)
plt.ylabel("Formation energy (eV)", fontsize=14)

if args.all:
    plt.legend(frameon=False)
    
plt.tight_layout()

suffix = ("_nc" if args.nc else "") + ("_qe" if args.qe else "")
plt.savefig(f"formation_energy-corrections-pydefect{suffix}.png", dpi=150)

# Print the (x, y) values of the intersection points
corr_status = "without corrections" if args.nc else "with corrections"
print(f"\nCharge-transition levels (intersections of the minimum curve, {corr_status}):")
if unique_intersections:
    for x_cross, y_cross, qi, qj in unique_intersections:
        print(f"  q={qi:+d}/{qj:+d}  ->  E_F = {x_cross:.4f} eV,  E_form = {y_cross:.4f} eV")
else:
    print("No transitions found within the plotted Fermi-level range.")
