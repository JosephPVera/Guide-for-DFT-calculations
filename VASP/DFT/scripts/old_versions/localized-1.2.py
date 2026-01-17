#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

import xml.etree.ElementTree as ET
import os
import argparse

tree = ET.parse('vasprun.xml')
root = tree.getroot()

# variables
VBM = 7.2945
CBM = 11.7449

"Usage: ----> localized.py                 # all information within the band gap (occupied, unoccupied, partially occupied), if they exist at all \
        ----> localized.py --occ           # only occupied sates within the the band gap, if they exist at all \
        ----> localized.py --nocc          # only unoccupied sates within the the band gap, if they exist at all \
        ----> localized.py --pocc          # only partially occupied sates within the the band gap, if they exist at all \
        ----> localized.py --band 5.4 11.3 # Modify the VBM and CBM"
        
"Code use information from vasprun.xml file"
"There are three sub codes:  \
       ----> The first code is used to find the values of spin, kpoints, and bands. \
       ----> The second code parse the vasprun.xml file (EIGENVAL information) and sort the information about Spin up, kpoint (up), band (up), Spin down \
              kpoint (down) and band (down), only filters energy values (column 1) between VBM and CBM following the break of 1.000 \
              in the column 2 (when continuity of 1.00 is broken)(HOMO-LUMO transition). That information is store in lists as band_index_list_up, \
              kpoint_list_up, spin_list_up, band_index_list_down, kpoint_list_down and spin_list_down. \
       ----> The third code use the band_index_list_up, kpoint_list_up, spin_list_up, band_index_list_down, kpoint_list_down and spin_list_down lists \
              and parse each value of the list for get the desired information."    
 
 
# Parse commands arguments for filter options
parser = argparse.ArgumentParser(description="Parse EIGENVAL and vasprun.xml files with optional filtering by occupancy label.")
parser.add_argument('--occ', action='store_true', help="Save only Occupied values")
parser.add_argument('--nocc', action='store_true', help="Save only Unoccupied values")
parser.add_argument('--pocc', action='store_true', help="Save only Partially Occupied values")
parser.add_argument('--band', nargs=2, type=float, default=[VBM, CBM], help="Specifies the values ​​for VBM and CBM. By default: VBM=7.2945 and CBM=11.7449")
args = parser.parse_args()
vbm, cbm = args.band

# Define filtering options based on arguments
filter_occupancy = []
if args.occ:
    filter_occupancy.append("Occupied")
if args.nocc:
    filter_occupancy.append("Unoccupied")
if args.pocc:
    filter_occupancy.append("Partially Occupied")
    

# Find the spin numbers, kpoint, and band in vasprun.xml
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


"Parsing the vasprun.xml for get information same to EIGENVAL file"
# Initialize lists to store information
energy_values = []
occupancy_list = []
occupation_status = {}

band_index_list_up = []
kpoint_list_up = []
spin_list_up = []

band_index_list_down = []
kpoint_list_down = []
spin_list_down = []

output_file_path = 'eigenval_infos.dat' 
with open(output_file_path, "w") as file:
    for spin_number in spin_numbers:
        occupation_status[spin_number] = {}  # Add key for each spin

        # Write a section header for each spin
        file.write("###########################################################\n")
        file.write(f"                           {'SPIN UP' if spin_number == 1 else 'SPIN DOWN'}                     \n")
        file.write("###########################################################\n")
        
        for kpoint_number in kpoint_numbers:
            spin_set = root.find(f".//set[@comment='spin {spin_number}']")
            if spin_set is not None:
                kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']")
                if kpoint_block is not None:
                    block_values, block_occu, block_status, band_indices = [], [], [], []

                    for band_index, child in enumerate(kpoint_block, 1):
                        if child.text:
                            columns = child.text.split()
                            if len(columns) >= 2:
                                energy = float(columns[0])
                                occupancy = float(columns[1])
                                # Determine occupancy status
                                if occupancy == 1.0:
                                    status = "Occupied"
                                elif occupancy > 0.9:
                                    status = "Occupied"
                                elif occupancy < 0.1:
                                    status = "Unoccupied"
                                else:
                                    status = "Partially Occupied"

                                # Store values
                                block_values.append(energy)
                                block_occu.append(occupancy)
                                block_status.append((energy, status))
                                band_indices.append(band_index)

                    if block_values: energy_values.append(block_values)
                    if block_occu: occupancy_list.append(block_occu)
                    if block_status:
                        occupation_status[spin_number][kpoint_number] = block_status

                    for idx in range(1, len(block_occu)):
                        if block_occu[idx - 1] == 1.0 and block_occu[idx] < 1.0:
                            start_idx = max(idx - 500, 0)
                            end_idx = min(idx + 500, len(block_occu))
                            energies_in_range = block_values[start_idx:end_idx]
                            occupancies_in_range = block_occu[start_idx:end_idx]
                            indices_in_range = band_indices[start_idx:end_idx]

                            file.write("###########################################################\n")
                            file.write(f"                          kpoint {kpoint_number}                   \n")
                            file.write("###########################################################\n")
                            file.write(f"{'Band':<10} {'Energy':<14} {'Occ':<10} {'Occupancy'}\n")
                            
                            for band_index, (energy, occupancy) in zip(indices_in_range, zip(energies_in_range, occupancies_in_range)):
                                if vbm <= energy <= cbm:
                                    label = "Occupied" if occupancy > 0.9 else "Unoccupied" if occupancy < 0.1 else "Partially Occupied"
                                    
                                    # Apply filter if set
                                    if not filter_occupancy or label in filter_occupancy:
                                        if spin_number == 1:
                                            band_index_list_up.append(band_index)
                                            kpoint_list_up.append(kpoint_number)
                                            spin_list_up.append(spin_number)
                                        elif spin_number == 2:
                                            band_index_list_down.append(band_index)
                                            kpoint_list_down.append(kpoint_number)
                                            spin_list_down.append(spin_number)
                                        
                                        file.write(f"{band_index:<10} {energy:<14.6f} {occupancy:<10.6f} {label}\n")
                else:
                    print(f"Block 'kpoint {kpoint_number}' not found in 'spin {spin_number}'.")
            else:
                print(f"Superblock 'spin {spin_number}' not found.")

        if spin_number == 1:
            file.write("\n\n")
                
print("Spin Up - Band index list:", band_index_list_up)
print("Spin Up - kpoint list:", kpoint_list_up)
print("Spin Up - Spin list:", spin_list_up)

print("Spin Down - Band index list:", band_index_list_down)
print("Spin Down - kpoint list:", kpoint_list_down)
print("Spin Down - Spin list:", spin_list_down)
print("################################################################################")
#print("The eigenval_infos.dat file has been saved.")


"Parsing the vasprun.xml file using the band_index_list_up, kpoint_list_up, spin_list_up, band_index_list_down, \
 kpoint_list_down lists and spin_list_down as inputs."
 
with open('vasprun_infos.dat', 'w') as file:

    # Spin Up Analysis
    if band_index_list_up and kpoint_list_up and spin_list_up:
        file.write("########################################################################\n")
        file.write("                               SPIN UP                                  \n")
        file.write("########################################################################\n")

        # Group information by k-point
        current_kpoint = None
        band_info = []
        
        for i in range(len(band_index_list_up)):
            spin_number = spin_list_up[i]        # input
            kpoint_number = kpoint_list_up[i]    # input
            band_number = band_index_list_up[i]  # input

            # Find the spin up (1) superblock
            spin_set = root.find(f".//set[@comment='spin{spin_number}']")

            if spin_set is not None:
                # Find the block corresponding to the kpoint
                kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']")
                
                if kpoint_block is not None:
                    # If we are in a different k-point from the previous one, write the accumulated information
                    if current_kpoint != kpoint_number:
                        if band_info:
                            # Write accumulated information of the previous k-point
                            file.write("\n########################################################################\n")
                            file.write(f"                               KPOINT {current_kpoint}                             \n")
                            file.write("########################################################################\n")
                            for band in band_info:
                                file.write(band)
                                
                            band_info = []  # Reset for the next k-point
                        
                        current_kpoint = kpoint_number  # Update the current k-point
                        
                    # Process the bands for this k-point
                    band_subblock = kpoint_block.find(f".//set[@comment='band {band_number}']")
                    
                    if band_subblock is not None:
                        band_info.append(f"\nInformation of {band_subblock.attrib['comment']}:\n")
                        band_info.append(f"{'index':<6} {'s':<10} {'p':<10} {'d':<10} {'tot':<10}\n")
                        
                        # Add information of the band
                        for j, child in enumerate(band_subblock):
                            columns = child.text.split()
                            total_sum = sum(float(value) for value in columns)
                            
                            # Set the decimals
                            formatted_values = [f"{float(value):.3f}" for value in columns]
                            formatted_sum = f"{total_sum:.3f}"
                            
                            # Only print if the total (s+p+d) is greater than 0.1
                            if float(formatted_sum) > 0.1:
                                band_info.append(f"{j + 1:<6} {formatted_values[0]:<10} {formatted_values[1]:<10} {formatted_values[2]:<10} {formatted_sum:<10}\n")
                    else:
                        band_info.append(f"Subblock 'band {band_number}' not found in 'kpoint {kpoint_number}'.\n")

        # Write the information of the last k-point if it exists
        if band_info:
            file.write("\n########################################################################\n")
            file.write(f"                               KPOINT {current_kpoint}                             \n")
            file.write("########################################################################\n")
            for band in band_info:
                file.write(band)
    
    # Spin Down Analysis
    if band_index_list_down and kpoint_list_down and spin_list_down:
        file.write("\n\n\n\n")
        file.write("########################################################################\n")
        file.write("                               SPIN DOWN                                \n")
        file.write("########################################################################\n")

        # Group information by k-point
        current_kpoint = None
        band_info = []
        
        for i in range(len(band_index_list_down)):
            spin_number = spin_list_down[i]        # input
            kpoint_number = kpoint_list_down[i]    # input
            band_number = band_index_list_down[i]  # input

            # Find the spin down (2) superblock
            spin_set = root.find(f".//set[@comment='spin{spin_number}']")

            if spin_set is not None:
                # Find the block corresponding to the kpoint
                kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']")
                
                if kpoint_block is not None:
                    # If we are in a different k-point from the previous one, write the accumulated information
                    if current_kpoint != kpoint_number:
                        if band_info:
                            # Write accumulated information of the previous k-point
                            file.write("\n########################################################################\n")
                            file.write(f"                               KPOINT {current_kpoint}                             \n")
                            file.write("########################################################################\n")
                            for band in band_info:
                                file.write(band)
                            band_info = []  # Reset for the next k-point
                        
                        current_kpoint = kpoint_number  # Update the current k-point
                        
                    # Process the bands for this k-point
                    band_subblock = kpoint_block.find(f".//set[@comment='band {band_number}']")
                    
                    if band_subblock is not None:
                        band_info.append(f"\nInformation of {band_subblock.attrib['comment']}:\n")
                        band_info.append(f"{'index':<6} {'s':<10} {'p':<10} {'d':<10} {'tot':<10}\n")
                        
                        # Add information of the band
                        for j, child in enumerate(band_subblock):
                            columns = child.text.split()
                            total_sum = sum(float(value) for value in columns)
                            
                            # Set the decimals
                            formatted_values = [f"{float(value):.3f}" for value in columns]
                            formatted_sum = f"{total_sum:.3f}"
                            
                            # Only print if the total is greater than 0.1
                            if float(formatted_sum) > 0.1:
                                band_info.append(f"{j + 1:<6} {formatted_values[0]:<10} {formatted_values[1]:<10} {formatted_values[2]:<10} {formatted_sum:<10}\n")
                    else:
                        band_info.append(f"Subblock 'band {band_number}' not found in 'kpoint {kpoint_number}'.\n")

        # Write the information of the last k-point if it exists
        if band_info:
            file.write("\n########################################################################\n")
            file.write(f"                               KPOINT {current_kpoint}                             \n")
            file.write("########################################################################\n")
            for band in band_info:
                file.write(band)
#print("The vasprun_infos.dat file has been saved.")


# Extract folder name from current directory
folder_name = os.path.basename(os.getcwd())
# Create 'localized' folder 
#localized_folder = f'localized-defects/{folder_name}/Data'
localized_folder = f'localized-defects/{folder_name}/Data'
if not os.path.exists(localized_folder):
    os.makedirs(localized_folder)

    # Save the results
output_file = os.path.join(localized_folder, f'localized_{folder_name}.dat')

# Concatenate eigenval_infos.dat and vasprun_infos.dat
with open(output_file, 'w') as combined_file:
    # Read and write the content of eigenval_infos.dat
    combined_file.write(f"Defect: {folder_name}\n")
    combined_file.write(f"\nVBM = {vbm} eV\n")
    combined_file.write(f"CBM = {cbm} eV\n\n\n")
    combined_file.write("###########################################################\n")
    combined_file.write("           vasprun.xml file (EIGENVAL information)                            \n")
    combined_file.write("###########################################################\n")
    with open(output_file_path, 'r') as eigenval_file:
        combined_file.write(eigenval_file.read())
    
    # Optionally add a separator for clarity
    combined_file.write("\n\n\n\n########################################################################\n")
    combined_file.write("                  vasprun.xml file (PROCAR information)\n")
    combined_file.write("########################################################################\n")
    
    # Read and write the content of vasprun_infos.dat
    with open('vasprun_infos.dat', 'r') as vasprun_file:
        combined_file.write(vasprun_file.read())

# Remove the eigenval_infos.dat and vasprun_infos.dat after finishing the calculations, 
files_to_remove = ['eigenval_infos.dat', 'vasprun_infos.dat']

for file in files_to_remove:
    try:
        os.remove(file)
#        print(f"The {file} has been removed.")
    except FileNotFoundError:
        print(f"The {file} file not found.")
    except Exception as e:
        print(f"Error deleting {file} file: {e}")
        
print(f"The localized_{folder_name}.dat file has been created.")
