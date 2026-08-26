#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2025-06

"""
Configuration Coordinate Diagram (CCD) builder and Huang-Rhys analysis.

Works with either VASP (default) or Quantum ESPRESSO (--qe) outputs.

Workflow this script expects:
  1. Ground state relaxed geometry + total energy E_g(Qg)
  2. Excited state relaxed geometry + total energy E_e(Qe)
  3. Single-point ground-state Hamiltonian at excited geometry -> E_g(Qe)
  4. Single-point excited-state Hamiltonian at ground geometry -> E_e(Qg)
  5. (Optional) a series of interpolated structures between the two
     minima, each with a single-point energy on the relevant surface,
     for a proper parabola fit instead of the two-point estimate.

Usage:
    - Fill in the INPUTS section below (paths to relaxed structures,
      and the four total energies from VASP or QE output files).
    - Optionally add interpolated (lambda, E_g, E_e) points for a
      real parabola fit; leave those lists empty to fall back to the
      two-point estimate.
    - Run:
        python plotccd.py            # VASP (default)
        python plotccd.py --qe       # Quantum ESPRESSO
    - Produces ccd.png and prints dQ, effective phonon energies,
      Huang-Rhys factors, and Debye-Waller factors for both branches.

Note on Stokes / anti-Stokes naming (see e.g. Huang, Ke & Lei,
J. Appl. Phys. 137, 134303 (2025), Fig. 5):
    Stokes shift (Delta S)       = relaxation energy on the EXCITED
                                    branch (dE_excited)
    anti-Stokes shift (Delta AS) = relaxation energy on the GROUND
                                    branch (dE_ground)
Both names are written to ccd.dat alongside the Relaxation_energy_*
labels so the file matches either convention.
"""

import argparse

import numpy as np
import matplotlib.pyplot as plt
from ase.io import read

# ---------------------------------------------------------------- #
# CLI -- pick the code the inputs below come from
# ---------------------------------------------------------------- #

parser = argparse.ArgumentParser(
    description="Build a configuration coordinate diagram (CCD) and "
                 "Huang-Rhys analysis from VASP or Quantum ESPRESSO energies."
)
parser.add_argument(
    "--qe", action="store_true",
    help="Use the Quantum ESPRESSO inputs/energies instead of VASP (default).",
)
args = parser.parse_args()

# ---------------------------------------------------------------- #
# INPUTS -- edit these for your system
# ---------------------------------------------------------------- #

# Relaxed structures. Filenames/format switch automatically with --qe.
if args.qe:
    # QE input files (ATOMIC_POSITIONS + CELL_PARAMETERS cards),
    # read with ASE's 'espresso-in' format.
    GROUND_STRUCT = "ground_state.in"
    EXCITED_STRUCT = "excited_state.in"
    READ_FORMAT = "espresso-in"
else:
    # VASP POSCAR files, read with ASE's 'vasp' format.
    GROUND_STRUCT = "POSCAR_ground"
    EXCITED_STRUCT = "POSCAR_excited"
    READ_FORMAT = "vasp"

# Total energies:
#   - VASP (default): as printed by OUTCAR/OSZICAR ("energy(sigma->0)"
#     or "free  energy   TOTEN"), already in eV.
#   - QE (--qe): as printed by QE ("!    total energy"), in Rydberg;
#     converted to eV automatically below.
RY_TO_EV = 13.605703976

#E_g_Qg = -1934.980784   # ground state Hamiltonian at ground geometry
#E_g_Qe = -1934.809417   # ground state Hamiltonian at excited geometry
#E_e_Qg = -1933.070423   # excited state Hamiltonian at ground geometry
#E_e_Qe = -1933.271245   # excited state Hamiltonian at excited geometry

# Optional: interpolated single-point energies for a real parabola
# fit near each minimum. lam = 0 at ground geometry, lam = 1 at
# excited geometry. Leave both lists empty ([]) to use the two-point
# method only. Fill these once, in the native units of whichever
# code produced them (eV for VASP, Ry for QE) -- the --qe flag
# controls whether the Ry->eV conversion below is applied.
lam_ground_branch = [0.000, 0.125, 0.250, 0.375, 0.500, 0.625, 0.750, 0.875, 1.000]
#E_ground_branch = [-1934.980784, -1934.977989, -1934.969964, -1934.956341, -1934.937106, -1934.912548, -1934.883567, -1934.849263, -1934.809417] # VASP
E_ground_branch = [-3971.35123692, -3971.35102213, -3971.35043852, -3971.34948852, -3971.34817434, -3971.34649790, -3971.34446085, -3971.34206465, -3971.33931072] #QE

lam_excited_branch = [0.000, 0.125, 0.250, 0.375, 0.500, 0.625, 0.750, 0.875, 1.000]
#E_excited_branch = [-1933.070423, -1933.120350, -1933.160452, -1933.194160, -1933.221428, -1933.242528, -1933.258358, -1933.268010, -1933.271245] # VASP
E_excited_branch = [-3971.21257337, -3971.21571612, -3971.21844021, -3971.22074576, -3971.22263282, -3971.22410140, -3971.22515168, -3971.22578418, -3971.22599987] #QE

if args.qe:
    E_ground_branch = [E * RY_TO_EV for E in E_ground_branch]
    E_excited_branch = [E * RY_TO_EV for E in E_excited_branch]

E_g_Qg, E_g_Qe = E_ground_branch[0], E_ground_branch[-1]
E_e_Qg, E_e_Qe = E_excited_branch[0], E_excited_branch[-1]

# ---------------------------------------------------------------- #
# 1. Mass-weighted displacement, dQ
# ---------------------------------------------------------------- #

atoms_g = read(GROUND_STRUCT, format=READ_FORMAT)
atoms_e = read(EXCITED_STRUCT, format=READ_FORMAT)

disp = atoms_e.get_positions() - atoms_g.get_positions()   # Angstrom
masses = atoms_g.get_masses()                              # amu

dQ2 = np.sum(masses[:, None] * disp**2)
dQ = np.sqrt(dQ2)                                           # amu^1/2 . Angstrom

print(f"ΔQ = {dQ:.4f} amu^(1/2)*Angstrom")
# ---------------------------------------------------------------- #
# 2. Relaxation energies (two-point method)
#    == Stokes / anti-Stokes shifts, see note at top of file
# ---------------------------------------------------------------- #

dE_ground = E_g_Qe - E_g_Qg   # ground state relaxes going Qe -> Qg  == anti-Stokes shift
dE_excited = E_e_Qg - E_e_Qe  # excited state relaxes going Qg -> Qe == Stokes shift

stokes_shift = dE_excited
anti_stokes_shift = dE_ground

print("")
print("---------------------------------------")
print("Relaxation energy")
print("---------------------------------------")
print(f"Anti-Stokes shift (ground)  = {dE_ground:.4f} eV")
print(f"Stokes shift (excited) = {dE_excited:.4f} eV")

# ---------------------------------------------------------------- #
# 3. Effective phonon frequencies, Huang-Rhys factors, and
#    Debye-Waller factors
#
#    hbar*omega_i = hbar * sqrt(2*dE_i) / dQ
#    S_i          = dE_i / (hbar*omega_i)
#    DW_i         = exp(-S_i)
#
# eV . amu^-1/2 . Angstrom^-1 -> meV conversion factor below is the
# standard prefactor used in the defect-CCD literature (e.g.
# Alkauskas et al., New J. Phys. 16, 073026 (2014)); double check
# against a published example before trusting the numeric value.
# ---------------------------------------------------------------- #

MEV_PER_UNIT = 64.654148  # meV per sqrt(eV) / (amu^1/2 . Angstrom)


def effective_frequency_meV(dE, dQ):
    """hbar*omega in meV from a relaxation energy (eV) and dQ."""
    return MEV_PER_UNIT * np.sqrt(2.0 * dE) / dQ


def huang_rhys(dE_eV, homega_meV):
    """Dimensionless Huang-Rhys factor. Same energy units, no conversion needed."""
    return (dE_eV * 1000.0) / homega_meV


def debye_waller_factor(S):
    """
    Debye-Waller factor W = exp(-S), the fraction of the total
    transition intensity carried by the zero-phonon line (T = 0 K,
    single effective mode approximation). S is the Huang-Rhys factor.
    """
    return np.exp(-S)


# --- two-point estimate, used unless a parabola fit overrides it ---
homega_g = effective_frequency_meV(dE_ground, dQ)
homega_e = effective_frequency_meV(dE_excited, dQ)


def fit_parabola_frequency(lam_list, E_list, lam_min, dQ):
    """
    Fit E = E0 + 0.5*k*(lam - lam_min)^2 * dQ^2 to interpolated points
    and return hbar*omega in meV. Falls back to None if fewer than 3
    points are provided.
    """
    if len(lam_list) < 3:
        return None
    lam = np.array(lam_list)
    E = np.array(E_list)
    Q = lam * dQ  # approximate: assumes linear interpolation in Q
    coeffs = np.polyfit(Q, E, 2)          # E = a*Q^2 + b*Q + c
    a = coeffs[0]                          # a = 0.5 * k  (eV / (amu.Angstrom^2))
    if a <= 0:
        return None
    k_eff = 2 * a
    # hbar*omega = hbar*sqrt(k_eff) in the same mass-weighted units
    return MEV_PER_UNIT * np.sqrt(k_eff)


fit_g = fit_parabola_frequency(lam_ground_branch, E_ground_branch, 0.0, dQ)
fit_e = fit_parabola_frequency(lam_excited_branch, E_excited_branch, 1.0, dQ)

if fit_g is not None:
    homega_g = fit_g
    #print("Using parabola fit for ground branch frequency.")
if fit_e is not None:
    homega_e = fit_e
    #print("Using parabola fit for excited branch frequency.")

S_g = huang_rhys(dE_ground, homega_g)
S_e = huang_rhys(dE_excited, homega_e)

DW_g = debye_waller_factor(S_g)
DW_e = debye_waller_factor(S_e)

print("")
print("---------------------------------------")
print("Effective phonon modes (frecuencies)")
print("---------------------------------------")
print(f"ℏω (ground) = {homega_g:.2f} meV")
print(f"ℏω (excited) = {homega_e:.2f} meV")
print("")
print("---------------------------------------")
print("Huang-Rhys factor")
print("---------------------------------------")
print(f"S (ground) = {S_g:.3f}")
print(f"S (excited) = {S_e:.3f}")
print("")
print("---------------------------------------")
print("Debye-Waller factor")
print("---------------------------------------")
print(f"D (ground) = {DW_g:.4f}")
print(f"D (excited) = {DW_e:.4f}")

zpl = E_e_Qe - E_g_Qg
print("")
print("---------------------------------------")
print("Zero Phonon Line (ZPL)")
print("---------------------------------------")
print(f"ZPL = {zpl:.4f} eV")
print("")
print("---------------------------------------")
print("Absorption and emission energy")
print("---------------------------------------")
print(f"E (absorption) = {E_e_Qg - E_g_Qg:.4f} eV")
print(f"E (emission) = {E_e_Qe - E_g_Qe:.4f} eV")

# ---------------------------------------------------------------- #
# 4. Plot the CCD
# ---------------------------------------------------------------- #

Q_g_min = 0.0
Q_e_min = dQ

k_g = (homega_g / MEV_PER_UNIT) ** 2   # back out curvature, eV/(amu.Angstrom^2)
k_e = (homega_e / MEV_PER_UNIT) ** 2

Q = np.linspace(-2.6 * dQ, 4.6 * dQ, 400)
E_ground_curve = E_g_Qg + 0.5 * k_g * (Q - Q_g_min) ** 2
E_excited_curve = E_e_Qe + 0.5 * k_e * (Q - Q_e_min) ** 2

fig, ax = plt.subplots(figsize=(6, 5))

ax.plot(Q, E_ground_curve, color="xkcd:blue", label="Ground state")
ax.plot(Q, E_excited_curve, color="xkcd:orange", label="Excited state")

# Overlay the actual computed points, so you can see how well the
# parabola tracks the real interpolated-geometry energies.
if len(lam_ground_branch) > 0:
    Q_ground_pts = np.array(lam_ground_branch) * dQ
    ax.plot(Q_ground_pts, E_ground_branch, "o", color="xkcd:blue",
            markerfacecolor="white", markersize=5)#, label="Ground state (data)")

if len(lam_excited_branch) > 0:
    Q_excited_pts = np.array(lam_excited_branch) * dQ
    ax.plot(Q_excited_pts, E_excited_branch, "o", color="xkcd:orange",
            markerfacecolor="white", markersize=5)#, label="Excited state (data)")

ax.plot(Q_g_min, E_g_Qg, "o", color="xkcd:blue")
ax.plot(Q_e_min, E_e_Qe, "o", color="xkcd:orange")

# Absorption: vertical line at Q_g_min from ground min to excited curve
E_abs_top = E_e_Qe + 0.5 * k_e * (Q_g_min - Q_e_min) ** 2
ax.annotate(
    "", xy=(Q_g_min, E_abs_top), xytext=(Q_g_min, E_g_Qg),
    arrowprops=dict(arrowstyle="->", color="xkcd:red", lw=1.5),
)
ax.text(Q_g_min, (E_abs_top + E_g_Qg) / 2, rf"E$_{{abs}}$ = {E_e_Qg - E_g_Qg:.2f} eV", rotation=90, va="center", ha="right", color="xkcd:black",)

# Emission: vertical line at Q_e_min from excited min to ground curve
E_em_bottom = E_g_Qg + 0.5 * k_g * (Q_e_min - Q_g_min) ** 2
ax.annotate(
    "", xy=(Q_e_min, E_em_bottom), xytext=(Q_e_min, E_e_Qe),
    arrowprops=dict(arrowstyle="->", color="xkcd:green", lw=1.5),
)
ax.text(Q_e_min, (E_em_bottom + E_e_Qe) / 2, rf"E$_{{em}}$ = {E_e_Qe - E_g_Qe:.2f} eV", rotation=-90, va="center", ha="left", color="xkcd:black",)

# ZPL
ax.plot([-0.5*dQ, 4*dQ], [E_e_Qe, E_e_Qe], color="xkcd:black", lw=0.8, linestyle="--")
ax.plot([-0.5*dQ, 4*dQ], [E_g_Qg, E_g_Qg], color="xkcd:black", lw=0.8, linestyle="--")
ax.annotate(
    "", xy=(3.8*dQ, E_g_Qg), xytext=(3.8*dQ, E_e_Qe),
    arrowprops=dict(arrowstyle="<->", color="xkcd:purple", lw=1.5),
)
ax.text(3.8*dQ, (E_g_Qg + E_e_Qe) / 2, rf"E$_{{ZPL}}$ = {zpl:.2f} eV", rotation=90, va="center", ha="right", color="xkcd:black",)

ax.set_xlabel(r"Configuration coordinate $Q$ (amu$^{1/2}$ $\AA$)", fontsize=14)
ax.set_ylabel("Total energy (eV)", fontsize=14)
#ax.set_title("Configuration coordinate diagram")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("ccd.png", dpi=150)
#print("Saved plot to ccd.png")

# ---------------------------------------------------------------- #
# 5. Save results to ccd.dat
# ---------------------------------------------------------------- #

with open("ccd.dat", "w") as f:
    f.write("Configuration Coordinate Diagram\n")
    f.write("\n")
    f.write(f"ΔQ = {dQ:.6f} amu^(1/2)*Angstrom\n")
    f.write("\n")
    f.write("-----------------------------------------\n")
    f.write(f"Zero Phonon Line (ZPL)\n")
    f.write("-----------------------------------------\n")
    f.write(f"ZPL = {zpl:.6f} eV\n")
    f.write("\n")
    f.write("-----------------------------------------\n")
    f.write(f"Absorption and emission energy\n")
    f.write("-----------------------------------------\n")
    f.write(f"E (absorption) = {E_e_Qg - E_g_Qg:.6f} eV\n")
    f.write(f"E (emission) = {E_e_Qe - E_g_Qe:.6f} eV\n")
    f.write("\n")
    f.write("-----------------------------------------\n")
    f.write(f"Relaxation energy\n")
    f.write("-----------------------------------------\n")
    #f.write(f"Relaxation_energy_ground_eV  {dE_ground:.6f}\n")
    #f.write(f"Relaxation_energy_excited_eV {dE_excited:.6f}\n")
    f.write(f"Anti-Stokes shift (ground) = {anti_stokes_shift:.6f} eV\n")
    f.write(f"Stokes shift (excited) = {stokes_shift:.6f} eV\n")
    f.write("\n")
    f.write("-----------------------------------------\n")
    f.write(f"Effective phonon modes (frecuencies)\n") # ℏω is the energy quantum of a mode, while ω or Ω is the angular frequency of the effective mode
    f.write("-----------------------------------------\n")
    f.write(f"ℏω (ground) = {homega_g:.4f} meV\n")
    f.write(f"ℏω (excited) = {homega_e:.4f} meV\n")
    f.write("\n")
    f.write("-----------------------------------------\n")
    f.write(f"Huang-Rhys factor\n")
    f.write("-----------------------------------------\n")   
    f.write(f"S (ground) = {S_g:.4f}\n")
    f.write(f"S (excited) = {S_e:.4f}\n")
    f.write("\n")
    f.write("-----------------------------------------\n")
    f.write(f"Debye-Waller factor\n") # e^(-S)
    f.write("-----------------------------------------\n")   
    f.write(f"D (ground) = {DW_g:.6f}\n")
    f.write(f"D (excited) = {DW_e:.6f}\n")
#print("Saved results to ccd.dat")
