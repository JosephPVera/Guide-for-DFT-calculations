#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from io import StringIO
from fractions import Fraction
import argparse

"Usage: ----> eigenplot.py                           # By default: VBM=7.2945 and CBM=11.7449 \
        ----> eigenplot.py --band 0.9 15.2           # Modify the VBM and CBM \
        ----> eigenplot.py --band 0.9 15.2 --res 0.9 # Modify the VBM and CBM, and also rescale for set to 0"
        
"Code for plot the Kohn-Sham states."

tree = ET.parse('vasprun.xml')
root = tree.getroot()

VBM = 7.2945
CBM = 11.7449
parser = argparse.ArgumentParser(description="Modify the VBM and CBM.")
parser.add_argument('--band', nargs=2, type=float, default=[VBM, CBM], help="Specifies the values ​​for VBM and CBM. By default: VBM=7.2945 and CBM=11.7449")
parser.add_argument('--res', type=float, default=0.0, help="Rescale respect to VBM")
args = parser.parse_args()
vbm, cbm = args.band
res = args.res 

# Find the spin numbers, kpoint and band in vasprun.xml
spin_numbers = []
kpoint_numbers = []
band_numbers = []

# Find the spin numbers
for spin_set in root.findall(".//set"):
    comment = spin_set.get('comment')
    if comment and comment.startswith('spin'):
        spin_number = int(comment.replace('spin', ''))
        if spin_number not in spin_numbers:
            spin_numbers.append(spin_number)

# Find the kpoint numbers
for spin_number in spin_numbers:
    spin_set = root.find(f".//set[@comment='spin{spin_number}']")
    if spin_set is not None:
        for kpoint_set in spin_set.findall(".//set"):
            comment = kpoint_set.get('comment')
            if comment and comment.startswith('kpoint'):
                kpoint_number = int(comment.replace('kpoint ', ''))
                if kpoint_number not in kpoint_numbers:
                    kpoint_numbers.append(kpoint_number)

# Find the band numbers
for spin_number in spin_numbers:
    spin_set = root.find(f".//set[@comment='spin{spin_number}']")
    if spin_set is not None:
        for kpoint_number in kpoint_numbers:
            kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']")
            if kpoint_block is not None:
                for band_set in kpoint_block.findall(".//set"):
                    comment = band_set.get('comment')
                    if comment and comment.startswith('band'):
                        band_number = int(comment.replace('band ', ''))
                        if band_number not in band_numbers:
                            band_numbers.append(band_number)

#print("List of spin_numbers:", spin_numbers)
#print("List of kpoint_numbers:", kpoint_numbers)
#print("List of band_numbers:", band_numbers)


# Store
results = []

results.append(f"{'Spin':<6} {'k-point':<10} {'Band':<10} {'tot':<10} {'sum':<10}")

# Iterate through lists of inputs spin numbers, kpoint and band (s, p and d orbitals)
for spin_number in spin_numbers:
    # Find the superblock. key word ---> <set comment="spin1"> 
    spin_set = root.find(f".//set[@comment='spin{spin_number}']")

    if spin_set is not None:
        for kpoint_number in kpoint_numbers:
            # find the block. key word ---> <set comment="kpoint 1">  
            kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']")
            
            if kpoint_block is not None:
                for band_number in band_numbers:
                    # find subblocks for sum the value and find the tot column and also compute the sum of the 5 biggest numbers of each band. key word ---> <set comment="band 1">
                    band_subblock = kpoint_block.find(f".//set[@comment='band {band_number}']")
                    
                    if band_subblock is not None:
                        total_sum = 0.0  # total sum
                        tot_values = []  # store tot
                        
                        # subblock
                        for i, child in enumerate(band_subblock):
                            # get the values of the columns
                            columns = child.text.split()
                            
                            # Convert to float to calculate the sum
                            total = float(columns[0]) + float(columns[1]) + float(columns[2])  
                            total_sum += total  # total sum
                            tot_values.append(total) 
                            
                        # Calculate the sum of the 5 values ​​closest to 1 (the sum of the 5 biggest numbers of each band)
                        closest_to_one = sorted(tot_values, key=lambda x: abs(x - 1))[:5]
                        closest_sum = sum(closest_to_one)
                        
                        results.append(f"{spin_number:<6} {kpoint_number:<10} {band_number:<10} {total_sum:<10.3f} {closest_sum:<10.3f}")
                        
                    else:
                        print(f"Subblock 'band {band_number}' not found in 'kpoint {kpoint_number}'.")
            else:
                print(f"Block 'kpoint {kpoint_number}' not found in 'spin{spin_number}'.")
    else:
        print(f"Superblock 'spin{spin_number}' not found.")

# energy and occupancy
energy_values = []
occupancy_list = []
for spin_number in spin_numbers:
    for kpoint_number in kpoint_numbers:
        # spin superblock
        spin_set = root.find(f".//set[@comment='spin {spin_number}']")  # key word ---> <set comment="spin 1"> before to <set comment="kpoint 1">
        
        if spin_set is not None:
            # kpoint block
            kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']") # key word ---> <set comment="kpoint 1"> after to <set comment="spin 1"> 
            
            if kpoint_block is not None:
                block_values = []  # temporal list to the energy
                block_occu = [] # temporal list to the occupancy
                for child in kpoint_block:
                    if child.text:
                        columns = child.text.split()
                        if len(columns) >= 2:
                            block_values.append(float(columns[0]))  
                            block_occu.append(float(columns[1]))
                if block_values: 
                    energy_values.append(block_values)
                if block_occu:
                    occupancy_list.append(block_occu)
                    
            else:
                print(f"Block 'kpoint {kpoint_number}' not found in 'spin {spin_number}'.") # dont confuse with the others blocks
        else:
            print(f"Superblock 'spin {spin_number}' not found.") # dont confuse with the others superblocks

# Create the total list by combining results and energy_values
total_results = []
for i, result in enumerate(results):
    if i == 0:
        total_results.append(f"{result:<10} {'Energy':<10} {'Occ':<10}")
    else:
        block_index = (i - 1) // len(band_numbers)  
        row_index = (i - 1) % len(band_numbers)  
        energy_value = energy_values[block_index][row_index] if block_index < len(energy_values) and row_index < len(energy_values[block_index]) else ''
        occupancy_value = occupancy_list[block_index][row_index] if block_index < len(occupancy_list) and row_index < len(occupancy_list[block_index]) else ''
        total_results.append(f"{result:<10} {energy_value:<10.3f} {occupancy_value:<10.3f}")
        
        
        # Blank line between blocks
        if row_index == len(band_numbers) - 1 and block_index < len(energy_values) - 1:
            total_results.append("")



with open('total_results.dat', 'w') as f:
    for total in total_results:
        f.write(total + '\n')
        
# print total results
#for total in total_results:
#    print(total)


def extract_kpoint_coordinates(tree):
    
    # Find the <varray name="kpointlist"> tag and extract k-point coordinates
    kpoint_coordinates = []
    kpointlist = root.find(".//varray[@name='kpointlist']")
    
    if kpointlist is not None:
        for v in kpointlist.findall("v"):
            coordinates = [float(coord) for coord in v.text.strip().split()]
            kpoint_coordinates.append(coordinates)
    else:
        print("The <varray name='kpointlist'> tag was not found in the file.")
    
    return kpoint_coordinates

def generate_x_labels(kpt_coords, line_break="\n"):
    result = []
    for k in kpt_coords:
        x_label = []
        for i in k:
            frac = Fraction(i).limit_denominator(10)
            if frac.numerator == 0:
                x_label.append("0")
            else:
                x_label.append(f"{frac.numerator}/{frac.denominator}")
        if x_label == ["0", "0", "0"]:
            result.append("Γ")
        else:
            result.append(line_break.join(x_label))
    return result

def plot_eigenvalues(file_name, kpoint_coordinates):
    with open(file_name, 'r') as file:
        content = file.readlines()

    content = ''.join(content[1:])  # Skip the first line
    blocks = content.strip().split('\n\n')

    num_blocks = len(blocks)

    blocks_up = blocks[:num_blocks // 2]
    blocks_down = blocks[num_blocks // 2:]

    kpoint_vals_up = []
    energy_vals_up = []
    colors_up = []
    
    kpoint_vals_down = []
    energy_vals_down = []
    colors_down = []

    for i, block in enumerate(blocks):
        data = pd.read_csv(StringIO(block), sep=r'\s+', header=None)

        if data.shape[1] >= 7:
            subset = data.iloc[:, [1, 5, 6]]  
            subset.columns = ['kpoint', 'Energy', 'occ']

            occupancy = subset['occ'].to_list()  
            rupture_point = next((j for j, val in enumerate(occupancy) if val < 1.0), None)
        
            if rupture_point is not None and rupture_point >= 10 and rupture_point < len(occupancy) - 10:
                kpoint_vals = subset['kpoint'][rupture_point - 14:rupture_point + 11].to_list()
                energy_vals = subset['Energy'][rupture_point - 14:rupture_point + 11].to_list()
                occupancy_group = occupancy[rupture_point - 14:rupture_point + 11]

                if i < num_blocks // 2:  
                    kpoint_vals_up.extend(kpoint_vals)
                    energy_vals_up.extend(energy_vals)
                    colors_up.extend(['blue' if val > 0.9 else 'red' if val < 0.1 else 'green' for val in occupancy_group])
                else:  
                    kpoint_vals_down.extend(kpoint_vals)
                    energy_vals_down.extend(energy_vals)
                    colors_down.extend(['blue' if val > 0.9 else 'red' if val < 0.1 else 'green' for val in occupancy_group])

    rescale_up = [valor - res for valor in energy_vals_up] # res for rescale respect to VBM, by default is 0. Use command--res
    rescale_down = [valor - res for valor in energy_vals_down] # res for rescale respect to VBM, by default is 0. Use command--res
    
    fig, axs = plt.subplots(1, 2, figsize=(10, 8))  

    # Generate formatted x-axis labels from kpoint_coordinates
    kpoint_labels = generate_x_labels(kpoint_coordinates)

    # Map each kpoint to its respective label
    unique_kpoints = sorted(set(kpoint_vals_up + kpoint_vals_down))
    x_tick_labels = [kpoint_labels[unique_kpoints.index(kpt)] if kpt in unique_kpoints else '' for kpt in unique_kpoints]
    
    # Subplot Spin up
    axs[0].scatter(kpoint_vals_up, rescale_up, color=colors_up, label='Spin Up', s=30) 
    axs[0].set_xlabel('K-point coordinates', fontsize=12)
    axs[0].set_title('Spin up', fontsize=12)
    axs[0].set_ylabel('Energy (eV)', fontsize=12)
    axs[0].set_xlim(min(kpoint_vals_up) - 0.5, max(kpoint_vals_up) + 0.5)
    axs[0].set_ylim(vbm - 1.7945 - res, cbm + 1.7551 - res)
    axs[0].axhspan(vbm -res , vbm - 1.7945 - res, color='lightblue', alpha=0.4)
    axs[0].axhspan(cbm - res, cbm + 1.7551 - res, color='thistle', alpha=0.4)
    axs[0].set_xticks(unique_kpoints)
    axs[0].set_xticklabels(x_tick_labels, rotation=0, fontsize=8, size=10)

    # Subplot Spin down
    axs[1].scatter(kpoint_vals_down, rescale_down, color=colors_down, label='Spin Down', s=30) 
    axs[1].set_xlabel('K-point coordinates', fontsize=12)
    axs[1].set_title('Spin down', fontsize=12)
    axs[1].tick_params(axis='y', which='both', left=True, right=False, labelleft=False)
    axs[1].set_xlim(min(kpoint_vals_down) - 0.5, max(kpoint_vals_down) + 0.5)
    axs[1].set_ylim(vbm - 1.7945 - res, cbm + 1.7551 - res)
    axs[1].axhspan(vbm - res, vbm - 1.7945 - res, color='lightblue', alpha=0.4)
    axs[1].axhspan(cbm - res, cbm + 1.7551 - res, color='thistle', alpha=0.4)
    axs[1].set_xticks(unique_kpoints)
    axs[1].set_xticklabels(x_tick_labels, rotation=0, fontsize=8, size=10)

    occupied_patch = plt.Line2D([0], [0], marker='o', color='w', label='Occupied', markerfacecolor='blue', markersize=10)
    unoccupied_patch = plt.Line2D([0], [0], marker='o', color='w', label='Unoccupied', markerfacecolor='red', markersize=10)
    partially_occupied_patch = plt.Line2D([0], [0], marker='o', color='w', label='Partially occupied', markerfacecolor='green', markersize=10)
    vbm_patch = plt.Line2D([0], [0], color='lightblue', label='VBM')
    cbm_patch = plt.Line2D([0], [0], color='thistle', label='CBM')
    plt.legend(handles=[occupied_patch, unoccupied_patch, partially_occupied_patch, vbm_patch, cbm_patch], bbox_to_anchor=(1.56, 0.7))
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.03)
    plt.tight_layout()
    plt.savefig('kohn-sham-states.png', dpi=150)

kpoint_coordinates = extract_kpoint_coordinates(tree)

# Plot eigenvalues with k-point coordinates and formatted labels
plot_eigenvalues('total_results.dat', kpoint_coordinates)

# Remove the total_results.dat file 
files_to_remove = ['total_results.dat']

for file in files_to_remove:
    try:
        os.remove(file)
#        print(f"The {file} has been removed.")
    except FileNotFoundError:
        print(f"The {file} file not found.")
    except Exception as e:
        print(f"Error deleting {file} file: {e}")
