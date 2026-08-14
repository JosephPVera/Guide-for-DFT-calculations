#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

"""
Birch-Murnaghan (3rd order) equation of state fitting.

Reads results.dat directly. Expected file format:

    # folder   a   volume   total_energy

Usage:

        python bm_eos_fit.py [--ev] [--cnv]
        
  --ev when the data in column total_energy is in eV.
  --cnv to convert from Ry to eV
"""

from __future__ import division, print_function
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

INPUTFILE = "results.dat"       
VOL_COL = 2          
ENERGY_COL = 3       
A_COL = 1            
OUT_PREFIX = "bm_eos"

if "--ev" in sys.argv and "--cnv" in sys.argv:
    print("Error: --ev and --cnv are mutually exclusive. Use only one.")
    sys.exit(1)

CONVERT_RY_TO_EV = "--cnv" in sys.argv
ENERGY_UNIT = "eV" if ("--ev" in sys.argv or CONVERT_RY_TO_EV) else "Ry"

RY_TO_EV = 13.605693009
EV = 1.6021766208e-19   # J
AA = 1e-10               # m
GPa = EV / (AA ** 3) * 1e-9  # eV/AA^3 -> GPa conversion factor

def birch_murnaghan(V, V0, E0, B0, B0p):
    """
    3rd-order Birch-Murnaghan equation of state.

    V   : volume array, Angstrom^3
    V0  : equilibrium volume
    E0  : equilibrium energy
    B0  : bulk modulus (eV/Angstrom^3)
    B0p : pressure derivative of B0 (dimensionless)
    """
    eta = (V0 / V) ** (2.0 / 3.0)
    return E0 + (9.0 * V0 * B0 / 16.0) * (
        (eta - 1.0) ** 3 * B0p
        + (eta - 1.0) ** 2 * (6.0 - 4.0 * eta)   # <-- fixed: was 4*(V0/V)**2/3
    )

def initial_guess(V, E):
    """
    Preliminary parabolic fit E = c0 + c1*V + c2*V^2 to get a much better
    starting point for (V0, E0, B0, B0p) than a fixed guess. Near the
    minimum, B0 relates to the curvature via B0 ~ V0 * d2E/dV2.
    """
    coeffs = np.polyfit(V, E, 2)
    c2, c1, c0 = coeffs
    V0 = -c1 / (2 * c2)
    E0 = np.polyval(coeffs, V0)
    B0 = V0 * (2 * c2)
    if B0 <= 0:
        B0 = 0.5  # fallback if curvature came out unphysical
    B0p = 4.0
    return V0, E0, B0, B0p

try:
    data = np.loadtxt(INPUTFILE, skiprows=1,
                       usecols=(A_COL, VOL_COL, ENERGY_COL))
except Exception as exc:
    print("Trouble reading data from '{0}': {1}".format(INPUTFILE, exc))
    sys.exit(1)

if data.ndim == 1:
    data = data.reshape(1, -1)

A = data[:, 0].copy()
V = data[:, 1].copy()
E = data[:, 2].copy()

if len(V) < 4:
    print("Warning: fewer than 4 points ({0}). The 4-parameter BM fit "
          "is under-determined with this little data.".format(len(V)))

if CONVERT_RY_TO_EV:
    E = E * RY_TO_EV
    print("Converted total_energy: Ry -> eV (--cnv)")

order = np.argsort(V)
A = A[order]
V = V[order]
E = E[order]

p0 = initial_guess(V, E)
#print("Initial guess (V0, E0, B0[eV/AA^3], B0'):", p0)

try:
    popt, pcov = curve_fit(birch_murnaghan, V, E, p0=p0, maxfev=20000)
except RuntimeError as exc:
    print("Fit did not converge:", exc)
    sys.exit(1)

V0, E0, B0, B0p = popt
perr = np.sqrt(np.diag(pcov))

e_fit = birch_murnaghan(V, *popt)
resid = E - e_fit
rmse = np.sqrt(np.mean(resid ** 2))

a_coeffs = np.polyfit(V, A, 2)
a0 = np.polyval(a_coeffs, V0)

da_dV = np.polyval(np.polyder(a_coeffs), V0)
a0_err = abs(da_dV) * perr[0]

lines = []
lines.append("Results from the Birch-Murnaghan fit")
lines.append("-------------------------------------------------")
lines.append("N points fitted: {0}".format(len(V)))
lines.append("")
lines.append("V0  (Angstrom^3)      = {0:.6f} +/- {1:.6f}".format(V0, perr[0]))
lines.append("a0  (Angstrom)        = {0:.6f} +/- {1:.6f}".format(a0, a0_err))
lines.append("E0  ({0})              = {1:.6f} +/- {2:.6f}".format(ENERGY_UNIT, E0, perr[1]))
lines.append("B0  ({0}/Angstrom^3)   = {1:.6f} +/- {2:.6f}".format(ENERGY_UNIT, B0, perr[2]))
if ENERGY_UNIT == "eV":
    lines.append("B0  (GPa)             = {0:.4f} +/- {1:.4f}".format(B0 * GPa, perr[2] * GPa))
lines.append("B0' (dimensionless)   = {0:.4f} +/- {1:.4f}".format(B0p, perr[3]))
lines.append("")
lines.append("Fit RMSE ({0})         = {1:.3e}".format(ENERGY_UNIT, rmse))

report = "\n".join(lines)
#print()
print(report)

with open(OUT_PREFIX + "_results.dat", "w") as f:
    f.write(report + "\n")

fig, ax1 = plt.subplots(figsize=(6, 5))

V_plot = np.linspace(V.min(), V.max(), 200)
ax1.plot(V_plot, birch_murnaghan(V_plot, *popt), 'k-', label='BM fit')
ax1.plot(V, E, 'o', color='tab:red', label='data')
ax1.axvline(V0, color='gray', ls='--', lw=0.8)
ax1.set_xlabel('Volume (Angstrom$^3$)', fontsize=14)
ax1.set_ylabel('Total energy ({0})'.format(ENERGY_UNIT), fontsize=14)
ax1.legend()
ax1.set_title('Birch-Murnaghan EOS fit')

fig.tight_layout()
fig.savefig(OUT_PREFIX + ".png", dpi=150)
