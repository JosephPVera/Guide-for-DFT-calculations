#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Usage:
    python3 s_occupations.py [--degeneracy]
    
Reconstruct per-band, per-k-point, per-spin electronic occupations from a
SIESTA .EIG file, analogous to the occupation column found in VASP's
EIGENVAL file.

SIESTA does not write occupations directly: the .EIG file only contains
eigenvalues and the Fermi level. The occupation of every state is a
deterministic function of (eigenvalue - E_F) and the smearing scheme/width
used in the run, so it can be reconstructed exactly. This script reads the
smearing settings directly from the .fdf input file, using these fdf
keywords:

    ElectronicTemperature   <value> <unit>   (e.g. "ElectronicTemperature 300 K";
                                              default: 300 K if absent)
    OccupationFunction      FD | MP          (default: FD)
    OccupationMPOrder       <integer>        (default: 1, only used for MP)
    Spin                    non-polarized | polarized | non-collinear |
                             spin-orbit      (default: non-polarized if absent)

In the SIESTA manual, the smearing of the electronic occupations is done,
for both FD and MP, using a single energy width defined by
ElectronicTemperature -- there is no separate "MP width".

The Spin keyword (SIESTA manual, "Spin polarization" section) sets how many
electrons each reconstructed state can hold: for the default non-polarized
case each (k-point, band) state in the .EIG file holds up to 2 electrons
(spin degenerate); for polarized (collinear), non-collinear, and spin-orbit
calculations, the .EIG file already lists each spin channel/spinor
separately, so each state holds up to 1 electron. This is derived
automatically from Spin, so there is no manual degeneracy switch to set.

The .EIG and .fdf files are found automatically in the current directory
"""

import argparse
import glob
import re
import sys

import numpy as np
from scipy.special import erfc, factorial
from numpy.polynomial.hermite import hermval

def find_single_file(pattern):
    matches = glob.glob(pattern)
    if not matches:
        sys.exit(f"No {pattern} file found in the current directory.")
    if len(matches) > 1:
        sys.exit(f"Multiple {pattern} files found ({matches}); "
                  f"keep only one in the working directory.")
    return matches[0]

# Preserving the original decimal precision of each .EIG token
_SCI_RE = re.compile(r"^[-+]?\d*\.(\d+)[eE]([-+]?\d+)$")
_PLAIN_RE = re.compile(r"^[-+]?\d*\.(\d+)$")
_DEFAULT_DECIMALS = 6

def decimals_needed(token):
    """Return how many decimal places are needed to write `token` (as found
    in the .EIG file) in plain decimal notation without losing precision.
    """
    m = _SCI_RE.match(token)
    if m:
        mantissa_decimals = len(m.group(1))
        exponent = int(m.group(2))
        return max(mantissa_decimals - exponent, 0)

    m = _PLAIN_RE.match(token)
    if m:
        return len(m.group(1))

    return _DEFAULT_DECIMALS

def parse_eig(path):
    """Parse a SIESTA .EIG file"""
    with open(path) as f:
        tokens = f.read().split()

    pos = 0
    Ef = float(tokens[pos]); pos += 1
    nbands = int(tokens[pos]); pos += 1
    nspin_header = int(tokens[pos]); pos += 1
    nk = int(tokens[pos]); pos += 1

    nspin = 2 if nspin_header == 2 else 1

    eigs = np.zeros((nk, nspin, nbands))
    decimals = np.zeros((nk, nspin, nbands), dtype=int)
    k_indices = np.zeros(nk, dtype=int)

    for ik in range(nk):
        k_indices[ik] = int(tokens[pos]); pos += 1
        for isp in range(nspin):
            for ib in range(nbands):
                tok = tokens[pos]; pos += 1
                eigs[ik, isp, ib] = float(tok)
                decimals[ik, isp, ib] = decimals_needed(tok)

    return Ef, eigs, k_indices, decimals

UNITS_TO_EV = {
    "ev": 1.0,
    "mev": 1.0e-3,
    "ry": 13.605693122994,
    "mry": 13.605693122994e-3,
    "hartree": 27.211386245988,
    "ha": 27.211386245988,
    "k": 8.617333262e-5,
    "kelvin": 8.617333262e-5,
    "j": 6.241509074e18,
}

def normalize_label(label):
    """Reproduce fdf's own label-matching rule: case-insensitive, and
    '-', '_', '.' are ignored."""
    return re.sub(r"[-_.]", "", label).lower()

def parse_fdf(path):
    fdf_dict = {}
    with open(path) as f:
        for raw_line in f:
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            tokens = line.split()
            if len(tokens) < 2:
                continue
            label = normalize_label(tokens[0])
            fdf_dict[label] = tokens[1:]
    return fdf_dict

def get_electronic_temperature_eV(fdf_dict):
    """Read ElectronicTemperature and convert to eV.
    Default (matching SIESTA's own default): 300 K."""
    key = normalize_label("ElectronicTemperature")
    if key not in fdf_dict:
        return 300.0 * UNITS_TO_EV["k"]
    tokens = fdf_dict[key]
    value = float(tokens[0])
    unit = tokens[1].lower() if len(tokens) > 1 else "k"
    if unit not in UNITS_TO_EV:
        sys.exit(f"Unrecognized unit '{unit}' for ElectronicTemperature.")
    return value * UNITS_TO_EV[unit]

def get_occupation_function(fdf_dict):
    """Read OccupationFunction (FD or MP). Default: FD."""
    key = normalize_label("OccupationFunction")
    if key not in fdf_dict:
        return "fd"
    return fdf_dict[key][0].lower()

def get_occupation_mp_order(fdf_dict):
    """Read OccupationMPOrder. Default: 1."""
    key = normalize_label("OccupationMPOrder")
    if key not in fdf_dict:
        return 1
    return int(fdf_dict[key][0])

SPIN_DEGENERACY = {
    "nonpolarized": 2.0,
    "polarized": 1.0,
    "colinear": 1.0,
    "collinear": 1.0,
    "noncolinear": 1.0,
    "noncollinear": 1.0,
    "spinorbit": 1.0,
}

def get_degeneracy(fdf_dict):
    """Read Spin and return the corresponding occupation degeneracy.
    Default: non-polarized (degeneracy 2.0) if Spin is absent."""
    key = normalize_label("Spin")
    if key not in fdf_dict:
        return SPIN_DEGENERACY["nonpolarized"]
    spin_value = normalize_label(fdf_dict[key][0])
    if spin_value not in SPIN_DEGENERACY:
        sys.exit(f"Unrecognized Spin value '{fdf_dict[key][0]}' "
                  f"(expected non-polarized, polarized, non-collinear, "
                  f"or spin-orbit).")
    return SPIN_DEGENERACY[spin_value]

# Occupation functions
def fermi_dirac(x):
    """Fermi-Dirac occupation, f(x) in [0, 1], x = (eps - Ef) / kT."""
    x = np.clip(x, -700.0, 700.0)  # avoid overflow in exp
    return 1.0 / (np.exp(x) + 1.0)

def methfessel_paxton(x, order):
    """Methfessel-Paxton occupation of a given order, f(x) in ~[0, 1].
    order = 0 reduces to a Gaussian-smeared step function (0.5*erfc(x)).
    Reference: Methfessel & Paxton, Phys. Rev. B 40, 3616 (1989).
    """
    f = 0.5 * erfc(x)
    if order > 0:
        exp_x2 = np.exp(-np.clip(x, -700.0, 700.0) ** 2)
        for n in range(1, order + 1):
            A_n = (-1) ** n / (factorial(n) * 4 ** n * np.sqrt(np.pi))
            coeffs = np.zeros(2 * n)
            coeffs[-1] = 1.0  # picks out H_{2n-1}
            H = hermval(x, coeffs)
            f = f + A_n * H * exp_x2
    return f

def main():
    parser = argparse.ArgumentParser(
        description="Reconstruct SIESTA band occupations from a .EIG file, "
                     "using the smearing and spin settings "
                     "(ElectronicTemperature, OccupationFunction, "
                     "OccupationMPOrder, Spin) read automatically from the "
                     ".fdf input. Result is always written to "
                     "occupancy.dat.")
    parser.parse_args()

    eig_file = find_single_file("*.EIG")
    fdf_file = find_single_file("*.fdf")

    Ef, eigs, k_indices, decimals = parse_eig(eig_file)
    nk, nspin, nbands = eigs.shape

    fdf_dict = parse_fdf(fdf_file)
    width = get_electronic_temperature_eV(fdf_dict)
    scheme = get_occupation_function(fdf_dict)
    order = get_occupation_mp_order(fdf_dict)
    degeneracy = get_degeneracy(fdf_dict)

    x = (eigs - Ef) / width

    if scheme == "fd":
        f = fermi_dirac(x)
    elif scheme == "mp":
        f = methfessel_paxton(x, order)
    else:
        sys.exit(f"Unsupported OccupationFunction '{scheme}' "
                  f"(expected FD or MP).")

    occ = degeneracy * f

    lines_out = [
        f"# EIG file: {eig_file}   fdf file: {fdf_file}",
        f"# Fermi energy (eV): {Ef:.6f}",
        f"# ElectronicTemperature: {width:.6f} eV   "
        f"OccupationFunction: {scheme.upper()}   "
        f"OccupationMPOrder: {order}   degeneracy: {degeneracy}",
        "# k-index  spin  band  eigenvalue(eV)  occupation",
    ]
    for ik in range(nk):
        for isp in range(nspin):
            for ib in range(nbands):
                dec = int(decimals[ik, isp, ib])
                eig_str = f"{eigs[ik, isp, ib]:.{dec}f}"
                lines_out.append(
                    f"{k_indices[ik]:6d}  {isp + 1:4d}  {ib + 1:5d}  "
                    f"{eig_str:>16}  {occ[ik, isp, ib]:10.6f}"
                )
        lines_out.append("")

    with open("occupancy.dat", "w") as f_out:
        f_out.write("\n".join(lines_out) + "\n")
    print(f"Saved file: occupancy.dat ")

if __name__ == "__main__":
    main()
