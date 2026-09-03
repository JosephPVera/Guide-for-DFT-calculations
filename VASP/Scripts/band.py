#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

import os
import glob
import logging
import sys
import numpy as np
import matplotlib.pyplot as plt
from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.bandstructure import BandStructureSymmLine, BandStructure, Spin

"""
Usage:
      python3 band.py [--y] [--band]
      
--band            # include the VBM and CBM limits
"""

def check_vasprun():
    "Find the vasprun.xml file(s)"
    directories = sorted(glob.glob("split-*")) or ["."]
    vasprun_files = []

    for directory in directories:
        for file_extension in ["vasprun.xml", "vasprun.xml.gz"]:
            vr_file_path = os.path.join(directory, file_extension)
            if os.path.exists(vr_file_path):
                vasprun_files.append(vr_file_path)
                break
            else:
                print(f"vasprun.xml file was not found in {directory}")

    return vasprun_files

def find_kpoints_file(directory):
    """Determine which file holds the high-symmetry path/labels"""
    kpoints_opt_path = os.path.join(directory, "KPOINTS_OPT")
    kpoints_path = os.path.join(directory, "KPOINTS")

    if os.path.exists(kpoints_opt_path):
        return kpoints_opt_path
    if os.path.exists(kpoints_path):
        return kpoints_path
    raise FileNotFoundError(f"No KPOINTS or KPOINTS_OPT file found in {directory}")

def compute_k_distance(kpoints):
    "Calculate the k-distance from the k-points, using the OUTCAR"
    "Value 1: 0 \
     Value 2: norm([i + 1] - [i]) = distance 1 \
     Value 3: norm([i + 2] - [i + 1]) + distance 1 = distance 2 \
     Value 4: norm([i + 3] - [i + 2]) + distance 1 + distance 2 = distance 3 \
     ..... "
    distances = [0.0]
    for i in range(1, len(kpoints)):
        dist = np.linalg.norm(kpoints[i].frac_coords - kpoints[i-1].frac_coords)
        distances.append(distances[-1] + dist)
    return distances

def save_dat(bs, directory="."):
    "Save band structure data"
    output_filename = os.path.join(directory, "band_data.dat")
    reference_energy = bs.efermi if bs.is_metal() else bs.get_vbm()["energy"]

    with open(output_filename, "w") as output_file:
        output_file.write("# Distance Energies (eV)\n")

        k_distances = compute_k_distance(bs.kpoints)

        for spin in [Spin.up, Spin.down] if bs.is_spin_polarized else [Spin.up]:
            for band in bs.bands[spin]:
                for distance, energy in zip(k_distances, band):
                    output_file.write(f"{distance:.8f} {energy - reference_energy:.8f}\n")
                output_file.write("\n")

    return output_filename

def print_repeated_values(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        first_block = []

        # Extract the first block starting from the second line
        for line in lines[1:]:
            if line.strip() == "":
                break
            first_block.append(line.strip())

        # Get the first column of the first block
        first_column = [line.split()[0] for line in first_block if line.strip()]

        # Find repeated values in the first column
        repeated_values = []
        seen_values = set()

        # Add the first value of the column to the list
        if first_column:
            repeated_values.append(first_column[0])

        for value in first_column:
            if value in seen_values:
                if value not in repeated_values:
                    repeated_values.append(value)
            else:
                seen_values.add(value)

        # Add the last value of the column to the list
        if first_column:
            repeated_values.append(first_column[-1])

        return repeated_values

def read_kpoints(file_path):
    labels = []
    with open(file_path, 'r') as file:
        lines = file.readlines()[4:]  # Ignore the first four lines of the header

        previous_label = None
        for line in lines:
            parts = line.split(maxsplit=3)
            if len(parts) == 4:
                current_label = parts[3].strip()

                # Replace \Gamma with $\Gamma$
                if current_label == "\\Gamma":
                    current_label = "$\\Gamma$"

                # Add label if it is not a consecutive duplicate
                if current_label != previous_label:
                    labels.append(current_label)
                previous_label = current_label

    return labels

def analyze_files(band_structure_path, kpoints_path):
    repeated_values = print_repeated_values(band_structure_path)

    # Call the function to read unique labels in KPOINTS / KPOINTS_OPT
    unique_labels = read_kpoints(kpoints_path)
    return repeated_values, unique_labels

def main():
    y_min = None
    y_max = None
    draw_band_lines = False

    for i, arg in enumerate(sys.argv):
        if arg == '--y' and i + 2 < len(sys.argv):
            try:
                y_min = float(sys.argv[i + 1])
                y_max = float(sys.argv[i + 2])
            except ValueError:
                print("Invalid y-axis limits. Please provide numerical values.")
                return
        if arg == '--band':
            draw_band_lines = True

    vasprun_files = check_vasprun()

    for vr_file in vasprun_files:
        directory = os.path.dirname(vr_file) or "."

        try:
            vasprun = Vasprun(vr_file)

            # Auto-detect whether the path/labels live in KPOINTS (PBE) or
            # KPOINTS_OPT (HSE06-style hybrid runs)
            kpoints_file = find_kpoints_file(directory)
            print(f"Using {kpoints_file} for the high-symmetry path/labels")

            bs = vasprun.get_band_structure(kpoints_filename=kpoints_file, line_mode=True)

            band_data_file = save_dat(bs, directory=directory)
            print(f"Data has been saved: {band_data_file}")

            # Analyze the band structure data
            repeated_values, unique_labels = analyze_files(band_data_file, kpoints_file)

            # Load data for the plot
            data = np.loadtxt(band_data_file)

            fig, ax = plt.subplots()

            is_block_start = np.concatenate(([True], np.diff(data[:, 0]) < 0))
            block_indices = np.where(is_block_start)[0]

            for i in range(len(block_indices)):
                if i < len(block_indices) - 1:
                    block_data = data[block_indices[i]:block_indices[i + 1]]
                else:
                    block_data = data[block_indices[i]:]  # Last block

                # Separate the valence band and the conduction band
                valence_band = block_data[block_data[:, 1] < 0]
                conduction_band = block_data[block_data[:, 1] > 0]

                # Plot VBM and CBM with different colors
                if len(valence_band) > 0:
                    ax.plot(valence_band[:, 0], valence_band[:, 1], linestyle='-', markersize=1, c='xkcd:blue')

                if len(conduction_band) > 0:
                    ax.plot(conduction_band[:, 0], conduction_band[:, 1], linestyle='-', markersize=1, c='xkcd:blue')

            ax.set_ylabel('Energy (eV)', fontsize=14)

            xticks = [data[np.isclose(data[:, 0], float(value), atol=1e-8)][0, 0] for value in repeated_values]
            xtick_labels = unique_labels 

            ax.set_xticks(xticks)
            ax.set_xticklabels(xtick_labels, fontsize=14)

            for x in xticks:
                ax.axvline(x=x, color='xkcd:black', linestyle='-', linewidth=0.4)

            if y_min is not None and y_max is not None:
                plt.ylim(y_min, y_max)

            plt.xlim(min(xticks), max(xticks))

            # Draw band lines if --band is specified
            if draw_band_lines:
                cbm_info = bs.get_cbm()
                vbm_info = bs.get_vbm()
                Gap = cbm_info["energy"] - vbm_info["energy"]
                plt.axhspan(0, Gap, color='xkcd:gray', alpha=0.4)
                plt.axhline(y=0.00, color='xkcd:green', linestyle='dashed')
                plt.axhline(y=Gap, color='xkcd:green', linestyle='dashed')

            plot_file = os.path.join(directory, 'band_structure_plot.png')
            plt.savefig(plot_file, dpi=200, bbox_inches='tight')
            plt.close(fig)

        except Exception as e:
            logging.error(f"ERROR processing {vr_file}: {str(e)}")

if __name__ == "__main__":
    main()
