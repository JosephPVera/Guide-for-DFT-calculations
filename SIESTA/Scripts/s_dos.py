#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Usage:

    python3 s_dos.py [--x] [--y] [--pdos] [--total] [--nres]
    
--total : to force a single summed curve. sum spin up + down
--nres : to disable this rescaling entirely and plot the raw energies

Plot the total Density of States (DOS) or the Projected DOS (PDOS) for a
given atom from SIESTA output files, for non-polarized, (collinear)
spin-polarized, non-collinear and spin-orbit calculations alike.

- Total DOS : read from a .DOS file.
- PDOS      : read from a .PDOS, summing
              over all orbitals belonging to the requested atom.
- The Fermi energy is always read from the .PDOS file.

Spin handling
-------------
SIESTA encodes the number of spin channels directly in the file itself,
so it can be read off exactly (same idea as s_occupancy.py deriving the
occupation degeneracy from Spin/.fdf -- here the source is the file, not
the .fdf):

    .DOS   -> number of channels = number of columns after the energy one
    .PDOS  -> number of channels = the <nspin> tag

with the SIESTA convention (see the DOS/PDOS section of the manual):

    1 channel  (Spin none)                 -> single DOS curve
    2 channels (Spin polarized)            -> DOS-up / DOS-down
    4 channels (Spin non-colinear/SOC)     -> DOS-up / DOS-down /
                                               Re{DOS-updown} / Im{DOS-updown}
                                               (the last two encode the Mx,
                                               My magnetization and are not
                                               part of the physical DOS;
                                               total DOS = up + down)   
"""

import argparse
import glob
import re
import sys
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np

# Angular momentum quantum number (l) -> orbital letter
L_LABELS = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g"}

SPIN_COLORS = ("tab:blue", "tab:red")
POLARIZED_LABELS = ("spin up", "spin down")

GAP_TOL = 1e-4  # eV, same tolerance used in s_bandplot.py


def normalize_label(label):
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

SPIN_VALUES = {
    "none": "non-polarized",
    "nonpolarized": "non-polarized",
    "polarized": "polarized",
    "colinear": "polarized",
    "collinear": "polarized",
    "noncolinear": "non-colinear",
    "noncollinear": "non-colinear",
    "spinorbit": "spin-orbit",
}

SPIN_NCHANNELS = {
    "non-polarized": 1,
    "polarized": 2,
    "non-colinear": 4,
    "spin-orbit": 4,
}

def get_spin_type(fdf_dict):
    key = normalize_label("Spin")
    if key not in fdf_dict:
        return "non-polarized"
    raw_value = fdf_dict[key][0]
    value = normalize_label(raw_value)
    if value not in SPIN_VALUES:
        sys.exit(f"Unrecognized Spin value '{raw_value}' in the .fdf "
                  f"(expected non-polarized/none, polarized/colinear, "
                  f"non-colinear, or spin-orbit).")
    return SPIN_VALUES[value]

def calc_name_for(spin_type, nspin):
    if spin_type == "polarized":
        return "Spin polarized"
    if spin_type == "non-colinear":
        return "Spin non-colinear"
    if spin_type == "spin-orbit":
        return "Spin spin-orbit"
    if nspin == 2:
        return "Spin polarized"
    if nspin == 4:
        return "Spin non-colinear/spin-orbit"
    return "Spin none"

def find_default_file(extension):
    candidates = sorted(glob.glob(f"*.{extension}"))
    if not candidates:
        return None
    if len(candidates) > 1:
        print(f"Warning: multiple .{extension} files found, using '{candidates[0]}'.")
        print(f"         (all candidates: {candidates})")
    return candidates[0]

def get_fermi_energy(pdos_file):
    """Read the Fermi energy (eV) from a .PDOS file."""
    try:
        root = ET.parse(pdos_file).getroot()
    except (OSError, ET.ParseError):
        sys.exit(f"Error: could not read/parse '{pdos_file}'.")

    fermi_tag = root.find("fermi_energy")
    if fermi_tag is None or fermi_tag.text is None:
        sys.exit(f"Error: no <fermi_energy> tag found in '{pdos_file}'.")

    return float(fermi_tag.text.strip())

def get_nspin(pdos_file):
    """Read <nspin> from a .PDOS(.xml) file: 1 (Spin none), 2 (Spin
    polarized) or 4 (Spin non-colinear / spin-orbit)"""
    try:
        root = ET.parse(pdos_file).getroot()
    except (OSError, ET.ParseError):
        sys.exit(f"Error: could not read/parse '{pdos_file}'.")
    tag = root.find("nspin")
    if tag is None or tag.text is None:
        return 1
    return int(tag.text.strip())

def parse_eig_eigenvalues(path):
    """Read every eigenvalue from a SIESTA .EIG file as a flat array"""
    with open(path) as f:
        tokens = f.read().split()

    pos = 0
    pos += 1  # Ef (unused here)
    nbands = int(tokens[pos]); pos += 1
    nspin_header = int(tokens[pos]); pos += 1
    nk = int(tokens[pos]); pos += 1
    nspin = 2 if nspin_header == 2 else 1

    eigs = []
    for _ik in range(nk):
        pos += 1  # k-index token
        for _isp in range(nspin):
            for _ib in range(nbands):
                eigs.append(float(tokens[pos])); pos += 1

    return np.array(eigs)

def classify_and_get_reference(eigenvalues, e_fermi, tol=GAP_TOL):
    """Decide whether the system is a metal or a semiconductor/insulator
    and return the energy reference to use. Same idea as
    s_bandplot.py's classify_and_get_reference, applied here to the .EIG
    eigenvalues instead of the .bands array.

    Returns (reference, is_semiconductor, vbm, cbm)."""
    occupied = eigenvalues[eigenvalues <= e_fermi]
    unoccupied = eigenvalues[eigenvalues > e_fermi]

    if occupied.size == 0 or unoccupied.size == 0:
        return e_fermi, False, None, None

    vbm = occupied.max()
    cbm = unoccupied.min()
    is_semiconductor = (cbm - vbm) > tol

    if is_semiconductor:
        return vbm, True, vbm, cbm
    return e_fermi, False, vbm, cbm

def get_energy_reference(fermi_energy):
    """Look for a .EIG file to classify the material (metal vs.
    semiconductor/insulator) and pick the corresponding energy reference
    and axis label. Falls back to E_F if no .EIG file is found."""
    eig_file = find_default_file("EIG")
    if eig_file is None:
        print("No .EIG file found -> cannot classify metal vs "
              "semiconductor/insulator; using E_F as the reference.")
        return fermi_energy, r"$E - E_F$ (eV)"

    eigenvalues = parse_eig_eigenvalues(eig_file)
    reference, is_semiconductor, vbm, cbm = classify_and_get_reference(
        eigenvalues, fermi_energy)

    if is_semiconductor:
        gap = cbm - vbm
        print(f"Detected a gap at E_F ({gap:.6f} eV) -> treating as "
              f"semiconductor/insulator.")
        print(f"VBM = {vbm:.6f} eV, CBM = {cbm:.6f} eV. Rescaling "
              f"energies to E - E_VBM.")
        return reference, r"$E - E_{VBM}$ (eV)"

    print("No gap found at E_F -> treating as metal. Rescaling energies "
          "to E - E_F.")
    return reference, r"$E - E_F$ (eV)"

def process_dos(filepath):
    """Read a .DOS file. The number of spin channels is inferred from the
    column count (SIESTA convention):
        2 columns -> Spin none              : energy, DOS
        3 columns -> Spin polarized         : energy, DOS-up, DOS-down
        5 columns -> Spin non-col. / SOC    : energy, DOS-up, DOS-down,
                                               Re{DOS-updown}, Im{DOS-updown}

    Returns (energy, channels, nspin) where channels is a dict that always
    has a 'total' entry, plus 'up'/'down' (and 'Re'/'Im' for the 5-column
    case) when more than one channel is present.
    """
    try:
        data = np.loadtxt(filepath)
    except OSError:
        sys.exit(f"Error: could not open file '{filepath}'.")
    except ValueError:
        sys.exit(f"Error: could not parse numeric columns from '{filepath}'.")

    ncols = data.shape[1]
    energy = data[:, 0]

    if ncols == 2:
        nspin = 1
        channels = {"total": data[:, 1]}
    elif ncols == 3:
        nspin = 2
        up, down = data[:, 1], data[:, 2]
        channels = {"up": up, "down": down, "total": up + down}
    elif ncols == 5:
        nspin = 4
        up, down = data[:, 1], data[:, 2]
        channels = {"up": up, "down": down, "total": up + down,
                    "Re": data[:, 3], "Im": data[:, 4]}
    else:
        sys.exit(f"Error: unexpected number of columns ({ncols}) in "
                  f"'{filepath}' (expected 2, 3 or 5).")

    return energy, channels, nspin

def process_pdos(filepath, atom_index):
    """Read a .PDOS file and return (energy, pdos_by_orbital, nspin)
    for the requested atom. pdos_by_orbital maps the orbital letter
    ('s', 'p', 'd', ...) to an array of shape (nspin, npoints), summed over
    all orbitals of that type (m, z) belonging to that atom."""
    try:
        root = ET.parse(filepath).getroot()
    except (OSError, ET.ParseError):
        sys.exit(f"Error: could not read/parse '{filepath}'.")

    energy_tag = root.find("energy_values")
    if energy_tag is None or energy_tag.text is None:
        sys.exit(f"Error: no <energy_values> tag found in '{filepath}'.")
    energy = np.array([float(v) for v in energy_tag.text.split()])
    npoints = energy.size

    nspin = get_nspin(filepath)

    orbitals = [
        orb for orb in root.findall("orbital")
        if int(orb.attrib["atom_index"].strip()) == atom_index
    ]
    if not orbitals:
        sys.exit(f"Error: no orbitals found for atom {atom_index} in "
                  f"'{filepath}'.")

    pdos_by_orbital = {}
    for orb in orbitals:
        data_tag = orb.find("data")
        if data_tag is None or data_tag.text is None:
            continue
        l = int(orb.attrib["l"].strip())
        label = L_LABELS.get(l, f"l{l}")

        # Each orbital's <data> holds nspin values per energy point.
        raw = np.array([float(v) for v in data_tag.text.split()])
        data = raw.reshape(npoints, nspin).T  # -> (nspin, npoints)

        if label not in pdos_by_orbital:
            pdos_by_orbital[label] = np.zeros((nspin, npoints))
        pdos_by_orbital[label] += data

    return energy, pdos_by_orbital, nspin

def plot_total_dos(ax, energy, channels, nspin, force_total):
    """Plot the total DOS. Only the genuinely polarized case (nspin == 2)
    is split into spin-resolved curves by default; non-polarized
    (nspin == 1) and non-colinear/spin-orbit (nspin == 4) are NOT
    polarized cases, so DOS-up == DOS-down for nspin == 4 (no exchange
    splitting) and only one of the two (DOS-up) is plotted -- see the
    module docstring."""
    show_split = (nspin == 2) and not force_total
    if show_split:
        ax.plot(energy, channels["up"], color=SPIN_COLORS[0],
                 linewidth=1.2, label=POLARIZED_LABELS[0])
        ax.plot(energy, -channels["down"], color=SPIN_COLORS[1],
                 linewidth=1.2, label=POLARIZED_LABELS[1])
        ax.legend()
    elif nspin == 1:
        ax.plot(energy, channels["total"], color="blue", linewidth=1.2)
    else:
        # nspin == 4 (or --total on a polarized run): DOS-up == DOS-down
        # for a non-polarized (non-colinear/spin-orbit) calculation, so
        # plot only DOS-up rather than summing.
        curve = channels["up"] if nspin == 4 else channels["total"]
        ax.plot(energy, curve, color="blue", linewidth=1.2)

def plot_pdos(ax, energy, pdos_by_orbital, nspin, force_total):
    """Plot the orbital-resolved PDOS in a fixed s, p, d, f, g, ... order
    (any other label found goes at the end). Only the genuinely polarized
    case (nspin == 2) is split into spin-resolved curves by default;
    non-polarized (nspin == 1) and non-colinear/spin-orbit (nspin == 4)
    are NOT polarized cases, so each orbital is always plotted as a
    single curve"""
    ordered_labels = [l for l in L_LABELS.values() if l in pdos_by_orbital]
    ordered_labels += [l for l in pdos_by_orbital if l not in ordered_labels]

    show_split = (nspin == 2) and not force_total

    for i, label in enumerate(ordered_labels):
        color = f"C{i}"
        data = pdos_by_orbital[label]  # (nspin, npoints)

        if show_split:
            ax.plot(energy, data[0], color=color, linewidth=1.2, ls="-",
                     label=f"{label} {POLARIZED_LABELS[0]}")
            ax.plot(energy, -data[1], color=color, linewidth=1.2, ls="--",
                     label=f"{label} {POLARIZED_LABELS[1]}")
        else:
            # nspin == 1: data[0] is the only channel. nspin == 4 (non-
            # colinear/spin-orbit, not polarized): Sz-up == Sz-down, so
            # data[0] alone is plotted instead of summing. nspin == 2
            # with --total: sum up+down for the genuine total.
            if nspin == 2:
                curve = data[0] + data[1]
            else:
                curve = data[0]
            ax.plot(energy, curve, color=color, linewidth=1.2,
                     label=f"{label} orbital")

    ax.legend()

def main():
    parser = argparse.ArgumentParser(
        description="Plot the total DOS (default) or the orbital-resolved "
                     "PDOS (s, p, d, ...) of a given atom. The Spin "
                     "keyword (non-polarized/polarized/non-colinear/"
                     "spin-orbit) is read from the .fdf, and the energy "
                     "axis is referenced to E_F (metal) or E_VBM "
                     "(semiconductor/insulator), detected automatically "
                     "from a .EIG file if present."
    )
    parser.add_argument(
        "--x",
        nargs=2,
        type=float,
        metavar=("XMIN", "XMAX"),
        default=None,
        help="Energy axis (x) limits, e.g. --x 0 10",
    )
    parser.add_argument(
        "--y",
        nargs=2,
        type=float,
        metavar=("YMIN", "YMAX"),
        default=None,
        help="DOS axis (y) limits, e.g. --y 1 15",
    )
    parser.add_argument(
        "--pdos",
        type=int,
        metavar="ATOM",
        default=None,
        help="Plot the orbital-resolved PDOS (s, p, d, ...) of the given "
             "atom index instead of the total DOS, e.g. --pdos 1",
    )
    parser.add_argument(
        "--total",
        action="store_true",
        help="Force a single summed curve for the genuinely polarized "
             "(2-channel) case too. Has no extra effect on non-polarized "
             "or non-colinear/spin-orbit calculations, which are always "
             "plotted as a single curve since they are not polarized "
             "cases.",
    )
    parser.add_argument(
        "--nres",
        action="store_true",
        help="Disable rescaling in all cases (plot raw energies from the "
             "file, no E_F/.EIG lookup). By default, rescaling to E - E_F "
             "(metal) or E - E_VBM (semiconductor/insulator) is always "
             "applied.",
    )
    args = parser.parse_args()

    pdos_file = find_default_file("PDOS")
    if pdos_file is None:
        sys.exit("Error: no .PDOS file found in the current directory.")

    fermi_energy = get_fermi_energy(pdos_file)

    fdf_file = find_default_file("fdf")
    if fdf_file is not None:
        spin_type = get_spin_type(parse_fdf(fdf_file))
    else:
        spin_type = None
        print("No .fdf file found -> cannot read the Spin keyword; "
              "non-colinear and spin-orbit cannot be told apart from the "
              "DOS/PDOS files alone (will be reported generically).")

    if args.nres:
        print("--nres flag set -> no rescaling applied, plotting raw energies.")
        reference, xlabel = 0.0, "E (eV)"
    else:
        reference, xlabel = get_energy_reference(fermi_energy)

    fig, ax = plt.subplots()#figsize=(8, 5))

    if args.pdos is not None:
        energy, pdos_by_orbital, nspin = process_pdos(pdos_file, args.pdos)
        energy = energy - reference

        calc_name = calc_name_for(spin_type, nspin)
        expected_nspin = SPIN_NCHANNELS.get(spin_type)
        if expected_nspin is not None and expected_nspin != nspin:
            print(f"Warning: .fdf declares 'Spin {spin_type}' (expected "
                  f"{expected_nspin} channel(s)) but '{pdos_file}' has "
                  f"{nspin} channel(s); ignoring the .fdf value for "
                  f"labeling and trusting the file's actual channel count "
                  f"instead.")
            calc_name = calc_name_for(None, nspin)
        print(f"{calc_name} calculation detected ({nspin} channel"
              f"{'s' if nspin != 1 else ''}).")
        if nspin == 4: None

        plot_pdos(ax, energy, pdos_by_orbital, nspin, args.total)

        label_title = f"PDOS — atom {args.pdos}"
        ylabel = "PDOS (states/eV)"
    else:
        dos_file = find_default_file("DOS")
        if dos_file is None:
            sys.exit("Error: no .DOS file found in the current directory.")
        energy, channels, nspin = process_dos(dos_file)
        energy = energy - reference

        calc_name = calc_name_for(spin_type, nspin)
        expected_nspin = SPIN_NCHANNELS.get(spin_type)
        if expected_nspin is not None and expected_nspin != nspin:
            print(f"Warning: .fdf declares 'Spin {spin_type}' (expected "
                  f"{expected_nspin} channel(s)) but '{dos_file}' has "
                  f"{nspin} channel(s); ignoring the .fdf value for "
                  f"labeling and trusting the file's actual channel count "
                  f"instead.")
            calc_name = calc_name_for(None, nspin)
        print(f"{calc_name} calculation detected ({nspin} channel"
              f"{'s' if nspin != 1 else ''}).")
        if nspin == 4: None

        plot_total_dos(ax, energy, channels, nspin, args.total)

        label_title = f"Total DOS" 
        ylabel = "DOS (states/eV)"

    ax.axhline(0, color="xkcd:black", linestyle=":", linewidth=0.6)
    ax.axvline(0, color="xkcd:black", linestyle="--", linewidth=0.8)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(label_title)

    if args.x is not None:
        ax.set_xlim(args.x[0], args.x[1])
    if args.y is not None:
        ax.set_ylim(args.y[0], args.y[1])

    fig.tight_layout()

    if args.pdos is not None:
        output_name = pdos_file.rsplit(".", 1)[0] + f"_PDOS_atom{args.pdos}.png"
    else:
        output_name = dos_file.rsplit(".", 1)[0] + "_DOS.png"
    fig.savefig(output_name, dpi=300)

if __name__ == "__main__":
    main()
