#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

from ase.io import read
import numpy as np
import os

"Code to find vacancy, substitutional or interstitial defects by comparing perfect/POSCAR with defect/POSCAR"

poscar_defect = read("POSCAR")                  
poscar_perfect = read("../perfect/POSCAR")       

# Get the lattice matrix to handle any crystal structure
lattice_matrix = poscar_defect.get_cell()

# Extract fractional positions and symbols
frac_positions_defect = poscar_defect.get_scaled_positions()
frac_positions_perfect = poscar_perfect.get_scaled_positions()
symbols_defect = poscar_defect.get_chemical_symbols()
symbols_perfect = poscar_perfect.get_chemical_symbols()

# Tolerance to compare the positions in different POSCAR's (for find the vacancy, substitutional, or interstitial atoms)
tolerance = 0.001

def cartesian_distance(frac_pos_a, frac_pos_b, lattice):
    "Calculate the Cartesian distance between two fractional positions considering the lattice."
    cart_pos_a = np.dot(frac_pos_a, lattice)
    cart_pos_b = np.dot(frac_pos_b, lattice)
    return np.linalg.norm(cart_pos_a - cart_pos_b)

# vacancies
def find_vacancy(frac_pos_a, frac_pos_b, symbols_a):  
    vacancies = []
    for i, pos_a in enumerate(frac_pos_a):
        found = False
        for pos_b in frac_pos_b:
            if cartesian_distance(pos_a, pos_b, lattice_matrix) < tolerance:
                found = True
                break
        if not found:
            vacancies.append((symbols_a[i], pos_a, i + 1))
    return vacancies

# substitutional
def find_susbstitutional(frac_pos_a, frac_pos_b, symbols_a, symbols_b):  
    susbstitutional = []
    for i, pos_a in enumerate(frac_pos_a):
        for j, pos_b in enumerate(frac_pos_b):
            if cartesian_distance(pos_a, pos_b, lattice_matrix) < tolerance:
                if symbols_a[i] != symbols_b[j]:
                    susbstitutional.append((symbols_a[i], symbols_b[j], pos_a, i + 1, j + 1))
                break
    return susbstitutional

# interstitial
def find_interstitial(frac_pos_a, frac_pos_b, symbols_a):  
    interstitial = []
    for i, pos_a in enumerate(frac_pos_a):
        found = False
        for pos_b in frac_pos_b:
            if cartesian_distance(pos_a, pos_b, lattice_matrix) < tolerance:
                found = True
                break
        if not found:
            interstitial.append((symbols_a[i], pos_a, i + 1))
    return interstitial

# find the closest neighbors to the defect 
def find_closest_atoms(target_frac_position, frac_positions, symbols):
    distances = []
    for i, frac_pos in enumerate(frac_positions):
        if not np.array_equal(target_frac_position, frac_pos):
            distance = cartesian_distance(target_frac_position, frac_pos, lattice_matrix)
            distances.append((distance, symbols[i], frac_pos, i + 1))

    distances.sort(key=lambda x: x[0])

    if distances:
        closest_distance = distances[0][0]
        same_distance_atoms = [atom for atom in distances if np.isclose(atom[0], closest_distance, atol=0.001)]
        return same_distance_atoms
    return []

# Find vacancy, substitutional or interstitial defects
vacancies = find_vacancy(frac_positions_perfect, frac_positions_defect, symbols_perfect)
susbstitutional = find_susbstitutional(frac_positions_defect, frac_positions_perfect, symbols_defect, symbols_perfect)
interstitial = find_interstitial(frac_positions_defect, frac_positions_perfect, symbols_defect)

# Get the name of the current folder
folder_name = os.path.basename(os.getcwd())

# Create 'localized' folder
localized_folder = f'localized-defects/{folder_name}/Data'
if not os.path.exists(localized_folder):
    os.makedirs(localized_folder)

# Save the results in localized_{folder_name}.dat
output_file = os.path.join(localized_folder, f'neighbor_atoms.dat')

with open(output_file, "w") as file:
    # Print vacancies
    if vacancies:
        for symbol, frac_position, index in vacancies:
            print(f"\nVacancy: V_{symbol}")
            print(f"Index in ../perfect/POSCAR: {index}")
            print(f"Position: {frac_position}")

            file.write(f"\nVacancy: V_{symbol}\n")
            file.write(f"Index in ../perfect/POSCAR: {index}\n")
            file.write(f"Position: {frac_position}\n")

            closest_atoms = find_closest_atoms(frac_position, frac_positions_defect, symbols_defect)

            print(f"\nClosest neighbors to the V_{symbol} defect in {folder_name}/POSCAR:")
            print(f"{'Index':<10} {'Atom':<10} {'Position':<30} {'Distance (A)':<10}")
            file.write(f"\nClosest neighbors to the V_{symbol} defect in {folder_name}/POSCAR:\n")
            file.write(f"{'Index':<10} {'Atom':<10} {'Position':<30} {'Distance (A)':<10}\n")
            for distance, neighbor_symbol, neighbor_frac_position, neighbor_index in closest_atoms:
                frac_pos_str = ' '.join(f"{coord:.6f}" for coord in neighbor_frac_position)
                print(f"{neighbor_index:<10} {neighbor_symbol:<10} {frac_pos_str:<30} {distance:<10.4f}")
                file.write(f"{neighbor_index:<10} {neighbor_symbol:<10} {frac_pos_str:<30} {distance:<10.4f}\n")
    else:
        print(f"\nThere are no vacancy defects in the {folder_name}/POSCAR")
        file.write(f"\nThere are no vacancy defects in the {folder_name}/POSCAR\n")

    # Print substitutionals
    if susbstitutional:
        for new_symbol, old_symbol, frac_position, old_index, new_index in susbstitutional:
            print("\n##################################################################")
            print(f"\nSubstitutional: {new_symbol}_{old_symbol}")
            print(f"Index in ../perfect/POSCAR: {new_index}")
            print(f"Index in {folder_name}/POSCAR: {old_index}")
            print(f"Position: {frac_position}")

            file.write("\n##################################################################\n")
            file.write(f"\nSubstitutional: {new_symbol}_{old_symbol}\n")
            file.write(f"Index in ../perfect/POSCAR: {new_index}\n")
            file.write(f"Index in {folder_name}/POSCAR: {old_index}\n")
            file.write(f"Position: {frac_position}\n")

            closest_atoms = find_closest_atoms(frac_position, frac_positions_defect, symbols_defect)

            for missed_atom in vacancies:
                missed_symbol, missed_position, missed_index = missed_atom
                if cartesian_distance(frac_position, missed_position, lattice_matrix) < tolerance:
                    closest_atoms.append((cartesian_distance(frac_position, missed_position, lattice_matrix), missed_symbol, missed_position, missed_index))

            if closest_atoms:
                closest_distance = closest_atoms[0][0]
                same_distance_atoms = [atom for atom in closest_atoms if np.isclose(atom[0], closest_distance)]
                same_distance_atoms.sort(key=lambda x: x[0])

                print(f"\nClosest neighbors to the {new_symbol}_{old_symbol} defect in {folder_name}/POSCAR:")
                print(f"{'Index':<10} {'Atom':<10} {'Position':<30} {'Distance (A)':<10}")
                file.write(f"\nClosest neighbors to the {new_symbol}_{old_symbol} defect in {folder_name}/POSCAR:\n")
                file.write(f"{'Index':<10} {'Atom':<10} {'Position':<30} {'Distance (A)':<10}\n")
                for distance, neighbor_symbol, neighbor_frac_position, neighbor_index in same_distance_atoms:
                    frac_pos_str = ' '.join(f"{coord:.6f}" for coord in neighbor_frac_position)
                    print(f"{neighbor_index:<10} {neighbor_symbol:<10} {frac_pos_str:<30} {distance:<10.4f}")
                    file.write(f"{neighbor_index:<10} {neighbor_symbol:<10} {frac_pos_str:<30} {distance:<10.4f}\n")
    else:
        print("\n##################################################################")
        print(f"\nThere are no substitutional defects in the {folder_name}/POSCAR")
        file.write("\n##################################################################\n")
        file.write(f"\nThere are no substitutional defects in the {folder_name}/POSCAR\n")

    # Print interstitials
    if interstitial:
        for symbol, frac_position, index in interstitial:
            print("\n##################################################################")
            print(f"Interstitial: {symbol}_i")
            print(f"Index in {folder_name}/POSCAR: {index}")
            print(f"Position: {frac_position}")

            file.write("\n##################################################################\n")
            file.write(f"Interstitial: {symbol}_i\n")
            file.write(f"Index in {folder_name}/POSCAR: {index}\n")
            file.write(f"Position: {frac_position}\n")

            closest_atoms = find_closest_atoms(frac_position, frac_positions_defect, symbols_defect)

            print(f"\nClosest neighbors to the {symbol}_i defect in {folder_name}/POSCAR:")
            print(f"{'Index':<10} {'Atom':<10} {'Position':<30} {'Distance (A)':<10}")
            file.write(f"\nClosest neighbors to the {symbol}_i defect in {folder_name}/POSCAR:\n")
            file.write(f"{'Index':<10} {'Atom':<10} {'Position':<30} {'Distance (A)':<10}\n")
            for distance, neighbor_symbol, neighbor_frac_position, neighbor_index in closest_atoms:
                frac_pos_str = ' '.join(f"{coord:.6f}" for coord in neighbor_frac_position)
                print(f"{neighbor_index:<10} {neighbor_symbol:<10} {frac_pos_str:<30} {distance:<10.4f}")
                file.write(f"{neighbor_index:<10} {neighbor_symbol:<10} {frac_pos_str:<30} {distance:<10.4f}\n")
    else:
        print("\n##################################################################")
        print(f"\nThere are no interstitial defects in the {folder_name}/POSCAR")
        file.write("\n##################################################################\n")
        file.write(f"\nThere are no interstitial defects in the {folder_name}/POSCAR\n")

print("\nDefect information was saved in neighbor_atoms.dat.")
