#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from io import StringIO
import argparse

tree = ET.parse('vasprun.xml')
root = tree.getroot()

# variables
VBM = 7.2945
CBM = 11.7449

"Code for plot the localized defects. Default Energy versus sum of the 5 heaviest values from tot (each band) (check PROCAR). "

"Usage: ----> locplot.py                 # By default: VBM=7.2945 and CBM=11.7449 \
        ----> locplot.py --band 0.9 15.2 # Modify the VBM and CBM \
        ----> locplot.py --tot           # Modify to use the column tot (s + p + d): Energies versus tot"

        
parser = argparse.ArgumentParser(description="Modify the VBM and CBM.")
parser.add_argument('--band', nargs=2, type=float, default=[VBM, CBM], help="Specifies the values ​​for VBM and CBM. By default: VBM=7.2945 and CBM=11.7449")
parser.add_argument("--tot", action="store_true", help="Use column 3 instead of column 4 in the subset.")
args = parser.parse_args()
vbm, cbm = args.band

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

#print("Lista de spin_numbers:", spin_numbers)
#print("Lista de kpoint_numbers:", kpoint_numbers)
#print("Lista de band_numbers:", band_numbers)


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

# store final results
final_result = []
for total in total_results:
    final_result.append(total)

# for total in final_result:
#     print(total)

def plot_localized(final_result, spin_numbers, kpoint_numbers):
    folder_name = os.path.basename(os.getcwd())
    localized_folder = f'localized-defects/{folder_name}/Figures'
    if not os.path.exists(localized_folder):
        os.makedirs(localized_folder)

    content = '\n'.join(final_result[1:])
    blocks = content.strip().split('\n\n')

    if len(spin_numbers) == 0 or len(kpoint_numbers) == 0:
        print("Error: Spin numbers or kpoint numbers are empty.")
        return

    total_combinations = len(spin_numbers) * len(kpoint_numbers)

    if len(blocks) > total_combinations:
        print(f"Warning: More blocks ({len(blocks)}) than combinations ({total_combinations}).")

    for i, block in enumerate(blocks):
        if i >= total_combinations:
            break

        data = pd.read_csv(StringIO(block), sep=r'\s+', header=None)
        
        "Column 0 ----> spin number, \
         Column 1 ----> kpoint number, \
         Column 2 ----> band number, \
         Column 3 ----> tot (s + p + d), \
         Column 4 ----> sum of the 5 heaviest values from tot, \
         Column 5 ----> energy values, \
         Column 6 ----> occupancies"
        if data.shape[1] >= 7:
            if args.tot:
                subset = data.iloc[:, [5, 3, 6]]  # column tot 
            else:
                subset = data.iloc[:, [5, 4, 6]] # colum sum the 5 heaviest values
                
            #subset = data.iloc[:, [5, 4, 6]]
            subset.columns = ['Energy', 'sum', 'occ']

            spin_index = i // len(kpoint_numbers)
            kpoint_index = i % len(kpoint_numbers)

            if kpoint_index >= len(kpoint_numbers):
                print(f"Warning: Index for kpoint exceeds available kpoints.")
                continue
            
            spin = spin_numbers[spin_index]
            kpoint = kpoint_numbers[kpoint_index]

            plt.figure(figsize=(10, 6))
            
            for j in range(len(subset['sum'])):
                if np.isfinite(subset['sum'].iloc[j]):
                    if subset['occ'].iloc[j] > 0.9:
                        color = 'blue'
                    elif subset['occ'].iloc[j] < 0.1:
                        color = 'red'
                    else:
                        color = 'green'
                    
                    plt.scatter(subset['Energy'].iloc[j], subset['sum'].iloc[j], marker='o', color=color)

            occupied_patch = plt.Line2D([0], [0], marker='o', color='w', label='Occupied', markerfacecolor='blue', markersize=10)
            unoccupied_patch = plt.Line2D([0], [0], marker='o', color='w', label='Unoccupied', markerfacecolor='red', markersize=10)
            partially_occupied_patch = plt.Line2D([0], [0], marker='o', color='w', label='Partially occupied', markerfacecolor='green', markersize=10)
            vbm_patch = plt.Line2D([0], [0], color='lightblue', label='VBM')
            cbm_patch = plt.Line2D([0], [0], color='thistle', label='CBM')
            plt.legend(handles=[occupied_patch, unoccupied_patch, partially_occupied_patch, vbm_patch, cbm_patch])

            plt.axvspan(subset['Energy'].min() - 0.9, vbm, color='lightblue', alpha=0.4)
            plt.axvspan(cbm, subset['Energy'].max() + 0.9, color='thistle', alpha=0.4)
            
            plt.xlabel('Energy', fontsize=14)
            plt.ylabel('Localization', fontsize=14)
            plt.xlim(subset['Energy'].min() - 0.9, subset['Energy'].max() + 0.9)

            if spin == 1:
                plt.title(f'Spin up - kpoint {kpoint}')
                plot_filename = f'Spin_up-kpoint_{kpoint}.png'
                output_file = os.path.join(localized_folder, plot_filename)
            else:
                plt.title(f'Spin down - kpoint {kpoint}')
                plot_filename = f'Spin_down-kpoint_{kpoint}.png'
                output_file = os.path.join(localized_folder, plot_filename)      
            plt.savefig(output_file, bbox_inches='tight', dpi=150)
            plt.close()
            print("Saving figures ... ")
        else:
            print(f"Block {i + 1} does not have enough columns.")

plot_localized(final_result, spin_numbers, kpoint_numbers)
