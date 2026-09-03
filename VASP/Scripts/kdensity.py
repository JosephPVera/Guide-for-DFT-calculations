#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2025-03

import os
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import argparse

def extract_toten(root):
    """
    Extract the last 'e_wo_entrp' energy from a vasprun.xml file.
    """
    energies = root.findall(".//i[@name='e_wo_entrp']")
    if energies:
        last_energy = energies[-1].text.strip()
        return float(last_energy)
    else:
        print(f"e_wo_entrp not found")
        return None


def extract_kdensity(subfolder):
    """
    Extract the k-density value from the subfolder name.
    Assuming the subfolder name is a number (e.g., '1', '2', '3', etc.), we'll convert it to a float.
    """
    try:
        kdensity_value = float(subfolder)
        return kdensity_value
    except ValueError:
        print(f"Could not extract k-density value from {subfolder}")
        return None


def extract_num_atoms(root):
    """
    Extract the number of atoms from a vasprun.xml file.
    """
    atoms_element = root.find(".//atoms")
    if atoms_element is not None:
        num_atoms = int(atoms_element.text.strip())
        return num_atoms
    else:
        print(f"Number of atoms not found in the file.")
        return None


def extract_data(directory):
    kdensity_values = []
    total_energies = {}

    for subfolder in sorted(os.listdir(directory)):
        vasprun_path = os.path.join(directory, subfolder, "vasprun.xml")

        if os.path.exists(vasprun_path):
            tree = ET.parse(vasprun_path)
            root = tree.getroot()
            energy = extract_toten(root)
            kdensity_value = extract_kdensity(subfolder)

            if energy is not None and kdensity_value is not None:
                kdensity_values.append(kdensity_value)
                total_energies[kdensity_value] = energy

    return kdensity_values, total_energies

def save_data_to_file(kdensity_values, perfect_energies, increased_energies, decreased_energies, relative_energy_increased, relative_energy_decreased, filename='kdensity_data.dat'):
    """
    Save the data to a .dat file with the specified columns.
    """
    with open(filename, 'w') as file:
        # Write the header with alignment
        file.write(f"{'K-density':<10} {'E_per':<10} {'E_inc':<10} {'E_dec':<10} {'E_rel_inc':<12} {'E_rel_dec':<12}\n")
        
        # Write the data with alignment
        for kdensity in kdensity_values:
            e_per = perfect_energies.get(kdensity, 0)
            e_inc = increased_energies.get(kdensity, 0)
            e_dec = decreased_energies.get(kdensity, 0)
            e_rel_inc = relative_energy_increased[kdensity_values.index(kdensity)] if kdensity in kdensity_values else 0
            e_rel_dec = relative_energy_decreased[kdensity_values.index(kdensity)] if kdensity in kdensity_values else 0
            
            file.write(f"{kdensity:<10} {e_per:<10.3f} {e_inc:<10.3f} {e_dec:<10.3f} {e_rel_inc:<12.3f} {e_rel_dec:<12.3f}\n")

def plot_relative_energies(kdensity_values, relative_energy_increased, relative_energy_decreased):
    plt.plot(kdensity_values, relative_energy_increased, marker='o', linestyle='-', color="xkcd:blue", label='Increased')
    plt.plot(kdensity_values, relative_energy_decreased, marker='o', linestyle='-', color="xkcd:red", label='Decreased')
    plt.xlabel(r'k-density ($1/Å^3$)', fontsize=16)
    plt.ylabel('Relative energy (meV)', fontsize=16)
    plt.legend()
    plt.tight_layout()
    plt.savefig('relative_energies_kdensity.png', dpi=150)
    plt.show()


def main():
    perfect_dir = 'kdensity-perfect'
    increased_dir = 'kdensity-increased'
    decreased_dir = 'kdensity-decreased'

    # Extract data from each directory
    kdensity_values, perfect_energies = extract_data(perfect_dir)
    _, increased_energies = extract_data(increased_dir)
    _, decreased_energies = extract_data(decreased_dir)

    # Calculate relative energies in meV
    relative_energy_increased = [np.abs(perfect_energies[kdensity] - increased_energies[kdensity]) * 1000 for kdensity in kdensity_values]
    relative_energy_decreased = [np.abs(perfect_energies[kdensity] - decreased_energies[kdensity]) * 1000 for kdensity in kdensity_values]

    # Save the data to a file
    save_data_to_file(kdensity_values, perfect_energies, increased_energies, decreased_energies, relative_energy_increased, relative_energy_decreased)

    # Plot results
    plot_relative_energies(kdensity_values, relative_energy_increased, relative_energy_decreased)

if __name__ == "__main__":
    main()

