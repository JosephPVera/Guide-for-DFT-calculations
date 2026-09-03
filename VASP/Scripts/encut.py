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

def extract_encut(root):
    """
    Extract the ENCUT value from a vasprun.xml file.
    """
    encut_element = root.find(".//i[@name='ENCUT']")
    if encut_element is not None:
        encut_value = int(float(encut_element.text.strip()))
        return encut_value
    else:
        print(f"ENCUT not found")
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
    encut_values = []
    total_energies = {}

    for subfolder in sorted(os.listdir(directory)):
        vasprun_path = os.path.join(directory, subfolder, "vasprun.xml")

        if os.path.exists(vasprun_path):
            tree = ET.parse(vasprun_path)
            root = tree.getroot()
            energy = extract_toten(root)
            encut_value = extract_encut(root)

            if energy is not None and encut_value is not None:
                encut_values.append(encut_value)
                total_energies[encut_value] = energy

    return encut_values, total_energies

def save_data_to_file(encut_values, perfect_energies, increased_energies, decreased_energies, relative_energy_increased, relative_energy_decreased, filename='encut_cutoff_data.dat'):
    """
    Save the data to a .dat file with the specified columns.
    """
    with open(filename, 'w') as file:
        file.write(f"{'ENCUT':<8} {'E_per':<10} {'E_inc':<10} {'E_dec':<10} {'E_rel_inc':<12} {'E_rel_dec':<12}\n")
        
        # Write the data with alignment
        for encut in encut_values:
            e_per = perfect_energies.get(encut, 0)
            e_inc = increased_energies.get(encut, 0)
            e_dec = decreased_energies.get(encut, 0)
            e_rel_inc = relative_energy_increased[encut_values.index(encut)] if encut in encut_values else 0
            e_rel_dec = relative_energy_decreased[encut_values.index(encut)] if encut in encut_values else 0
            
            file.write(f"{encut:<8} {e_per:<10.3f} {e_inc:<10.3f} {e_dec:<10.3f} {e_rel_inc:<12.3f} {e_rel_dec:<12.3f}\n")

def plot_encut_vs_total_energy_per_atom(directory):
    encut = []
    energy_per_atom = []
    
    # Analyze all subfolders in the current directory
    subfolders = sorted(os.listdir(directory))
    
    for subfolder in subfolders:
        vasprun_path = os.path.join(directory, subfolder, "vasprun.xml")
        
        if os.path.exists(vasprun_path):
            tree = ET.parse(vasprun_path)
            root = tree.getroot()
            energy = extract_toten(root)
            num_atoms = extract_num_atoms(root)
            
            # Collect ENCUT, total energy, and number of atoms values
            encut_value = extract_encut(root)
            if energy is not None and encut_value is not None and num_atoms is not None:
                encut.append(encut_value)
                energy_per_atom.append(energy / num_atoms)  # Total Energy per Atom

    plt.figure(figsize=(8, 6))
    plt.plot(encut, energy_per_atom, marker='o', linestyle='-', color="xkcd:blue")
    plt.xlabel('Energy cutoff (eV)', fontsize=16)
    plt.ylabel('Total Energy per Atom (eV)', fontsize=16)
    plt.tight_layout()
    plt.savefig('total_energies.png', dpi=150)
    plt.show()

def plot_relative_energies(encut_values, relative_energy_increased, relative_energy_decreased):
    #plt.figure(figsize=(8, 6))
    plt.plot(encut_values, relative_energy_increased, marker='o', linestyle='-', color="xkcd:blue", label='Increased')
    plt.plot(encut_values, relative_energy_decreased, marker='o', linestyle='-', color="xkcd:red", label='Decreased')
    plt.xlabel('Energy cutoff (eV)', fontsize=16)
    plt.ylabel('Relative energy (meV)', fontsize=16)
    plt.legend()
    plt.tight_layout()
    plt.savefig('relative_energies.png', dpi=150)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Plot ENCUT vs energy data")
    parser.add_argument('--tot', action='store_true', help="Plot ENCUT vs Total Energy per Atom on the current folder")
    args = parser.parse_args()
    
    if args.tot:
        # if --tot flag is provided
        current_dir = os.getcwd()
        plot_encut_vs_total_energy_per_atom(current_dir)    
    else:  
        perfect_dir = 'cutoff-perfect'
        increased_dir = 'cutoff-increased'
        decreased_dir = 'cutoff-decreased'

        # Extract data from each directory
        encut_values, perfect_energies = extract_data(perfect_dir)
        _, increased_energies = extract_data(increased_dir)
        _, decreased_energies = extract_data(decreased_dir)

        # Calculate relative energies in meV
        relative_energy_increased = [np.abs(perfect_energies[encut] - increased_energies[encut]) * 1000 for encut in encut_values]
        relative_energy_decreased = [np.abs(perfect_energies[encut] - decreased_energies[encut]) * 1000 for encut in encut_values]

        # Save the data to a file
        save_data_to_file(encut_values, perfect_energies, increased_energies, decreased_energies, relative_energy_increased, relative_energy_decreased)

        # Plot results
        plot_relative_energies(encut_values, relative_energy_increased, relative_energy_decreased)

if __name__ == "__main__":
    main()
