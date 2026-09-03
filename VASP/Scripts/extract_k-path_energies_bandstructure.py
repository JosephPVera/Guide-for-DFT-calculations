#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

import os
import glob
import logging
import sys
import numpy as np
from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.bandstructure import BandStructureSymmLine, BandStructure, Spin
import warnings

"The code use the vasprun.xml file, also is possible check the information in EIGENVALUE file"
"In vasprun.xml search the key word as <kpoints> for check the k-path and >band< for check the energies"

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, message="No POTCAR file with matching TITEL fields was found")

def check_vasprun():
    "Find the vasprun.xml file"
    directories = sorted(glob.glob("split-*")) or ["."]
    vasprun_files = []

    for directory in directories:
        for file_extension in ["vasprun.xml", "vasprun.xml.gz"]:
            vr_file_path = os.path.join(directory, file_extension)
            if os.path.exists(vr_file_path):
                vasprun_files.append(vr_file_path) 
                break
            else:
                print("vasprun.xml file was not found")

    return vasprun_files

def compute_k_distance(kpoints):
    "Calculate the k-distance from the k-points"
    "First value ---> Kpoint1 \
     Second value ---> norm(kpoint2 - Kpoint1) \
     Third value ---> norm(kpoint3 - Kpoint2) + Second value \
     Fourth value ---> norm(kpoint4 - Kpoint3) + Third value \
     ..... "
    distances = [0.0]
    for i in range(1, len(kpoints)):
        dist = np.linalg.norm(kpoints[i].frac_coords - kpoints[i-1].frac_coords)
        distances.append(distances[-1] + dist)
    return distances

def save_dat(bs, prefix=None, directory=None):
    "Save band structure data"
    "Reference energy in semiconductors is the VBM"
    "The energies is saved in blocks: first block is band 1, second block is band 2, and so on"
    output_filename = os.path.join(directory or ".", "band_structure.dat")
    reference_energy = bs.efermi if bs.is_metal() else bs.get_vbm()["energy"] # Identify the reference energy, if is a Metal or semiconductors
    
    with open(output_filename, "w") as output_file:
        output_file.write("# Distance Energies (eV)\n")

        k_distances = compute_k_distance(bs.kpoints)

        # Extract and write energies (eigenvalues) for both spin up and spin down bands
        for spin in [Spin.up, Spin.down] if bs.is_spin_polarized else [Spin.up]:
            for band in bs.bands[spin]:
                for distance, energy in zip(k_distances, band):
                    output_file.write(f"{distance:.8f} {energy - reference_energy:.8f}\n")
#                    print(reference_energy) # Check the value of reference energy
                output_file.write("\n")

    return output_filename

def main():

    # Find vasprun.xml files
    vasprun_files = check_vasprun()
    
    for vr_file in vasprun_files:
        # Parse the vasprun.xml file to get band structure
        try:
            vasprun = Vasprun(vr_file)
            bs = vasprun.get_band_structure()

            # Save the data
            save_dat(bs, prefix=os.path.basename(vr_file).split('.')[0], directory='.')
            print("Data has been saved")

        except Exception as e:
            logging.error(f"ERROR processing {vr_file}: {str(e)}")

    

if __name__ == "__main__":
    main()
