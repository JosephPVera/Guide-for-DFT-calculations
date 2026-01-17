#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

import xml.etree.ElementTree as ET
import os

"Code use information from EIGENVAL and vasprun.xml"
"There are three sub codes:  \
       ----> The first code is a counter of superblock, blocks and subblocks in vasprun.xml. \
       ----> The second code parse the EIGENVAL file and sort the information about Spin up, kpoint (up), band (up), Spin down \
              kpoint (down) and band (down), only filters energy values (column 2 and 3) between VBM and CBM following the break of 1.000 \
              in the column 4 and 5 (when continuity of 1.00 is broken)(HOMO-LUMO transition). That information is store in lists as band_index_list_up, \
              kpoint_list_up, spin_list_up, band_index_list_down, kpoint_list_down and spin_list_down. \
       ----> The third code use the band_index_list_up, kpoint_list_up, spin_list_up, band_index_list_down, kpoint_list_down and spin_list_down lists \
              and parse each value of the list for get the desired information."
    

input_file_path = 'EIGENVAL'  
output_file_path = 'eigenval_infos.dat' 

tree = ET.parse('vasprun.xml')
root = tree.getroot()



"Counters"
"Superblock (Spin), block (kpoint) and subblock (band) counters"
# Key words in vasprun.xml: ---->  superblock Spin up: <set comment="spin1">
#                           ---->  superblock Spin down: <set comment="spin2">
#                           ---->  block kpoint N: <set comment="kpoint 1">
#                           ---->  subblock band N: <set comment="band 1">
superblock_count = 0
block_count = 0
subblock_count = 0

# Search for superblocks (spin1 and spin2)
for spin_set in root.findall(".//set[@comment='spin1']") + root.findall(".//set[@comment='spin2']"):
    superblock_count += 1
    
    # Search for blocks (kpoints) within each superblock
    for kpoint in spin_set.findall(".//set"):
        if 'kpoint' in kpoint.get('comment', ''):
            block_count += 1
            
            # Search for subblocks (bands) within each block
            for band in kpoint.findall(".//set"):
                if 'band' in band.get('comment', ''):
                    subblock_count += 1

# Print the results
print(f'Superblocks (Spin up and Spin down): {superblock_count}')
print(f'Blocks (kpoints) per superblock: {block_count / 2:.0f}')
print(f'Subblocks (bands) per superblock: {subblock_count / 2:.0f}')
print("##########################################################################################")





"Parsing the EIGENVAL file"
# Initialize variables
block_length = 0
blocks = []
VBM = 7.2945
CBM = 11.7449

# Lists to store Spin up, kpoint (up), band (up), Spin down, kpoint (down) and band (down)
band_index_list_up = []
kpoint_list_up = []
spin_list_up = []

band_index_list_down = []
kpoint_list_down = []
spin_list_down = []

# Read the file and store the blocks
with open(input_file_path, 'r') as file:
    # Skip the first 5 lines
    for _ in range(5):
        next(file)

    # Read line 6 to get the block size, third value
    block_info = next(file).strip()
    if block_info:
        values = block_info.split()
        if len(values) >= 3:
            block_length = int(values[2]) + 1  # Block length + 1 for the extra blank line
        else:
            raise ValueError("Line 6 does not have enough values.")

    # Skip line 7 (blank line)
    next(file)

    # Read the rest of the file
    lines = file.readlines()

    # Store blocks
    for i in range(0, len(lines), block_length + 1):  # +1 for the blank line between blocks
        block = lines[i:i + block_length]  # Get the block
        blocks.append(block)

# Function to analyze each block 
def analizar_bloque(bloque, bloque_num, output_file):
    # Write block header
    output_file.write("###########################################################\n")
    output_file.write(f"                          kpoint {bloque_num}                   \n")
    output_file.write("###########################################################\n")
    output_file.write(bloque[0].strip() + "\n")  # Write the first line (k-point coordinates) of each block
    
    # Ignore the first line (k-point coordinates) and process the following lines in the block
    datos = [line.split() for line in bloque[1:]]

    # Convert columns 1, 2, 3, 4, and 5 to lists of numbers
    indices_banda = [int(row[0]) for row in datos]
    energia_spin_up = [float(row[1]) for row in datos]
    energia_spin_down = [float(row[2]) for row in datos]
    ocupacion_spin_up = [float(row[3]) for row in datos]
    ocupacion_spin_down = [float(row[4]) for row in datos]

    # Look for the break point in spin up occupancy
    for i, ocupacion in enumerate(ocupacion_spin_up):
        if ocupacion != 1.0:
            output_file.write("\nBand(up)   Energy(up)     Occ(up)    Occupancy\n")
            start = max(0, i - 20) # above the break of 1.000
            end = min(len(indices_banda), i + 20) # below the break of 1.000
            for j in range(start, end):
                if VBM < energia_spin_up[j] < CBM: # Compare the column 2 with VBM and CBM
                    # Store band index, k-point, and spin for spin up
                    band_index_list_up.append(indices_banda[j])
                    kpoint_list_up.append(bloque_num)
                    spin_list_up.append(1)  # 1 for spin up, important to store in the list
                    occupation_status = (
                        "Occupied" if ocupacion_spin_up[j] > 0.9 else
                        "Unoccupied" if ocupacion_spin_up[j] < 0.1 else
                        "Partially Occupied"
                    )
                    output_file.write(f"{indices_banda[j]:<10} {energia_spin_up[j]:<14.6f} {ocupacion_spin_up[j]:<10.6f} {occupation_status}\n")
            break

    # Look for the break point in spin down occupancy
    for i, ocupacion in enumerate(ocupacion_spin_down):
        if ocupacion != 1.0:
            output_file.write("\nBand(down) Energy(down)   Occ(down)  Occupancy\n")
            start = max(0, i - 20) # above the break of 1.000
            end = min(len(indices_banda), i + 20) # below the break of 1.000
            for j in range(start, end):
                if VBM < energia_spin_down[j] < CBM: # Compare the column 3 with VBM and CBM
                    # Store band index, k-point, and spin for spin down
                    band_index_list_down.append(indices_banda[j])
                    kpoint_list_down.append(bloque_num)
                    spin_list_down.append(2)  # 2 for spin down, important to store in the list
                    occupation_status = (
                        "Occupied" if ocupacion_spin_down[j] > 0.9 else
                        "Unoccupied" if ocupacion_spin_down[j] < 0.1 else
                        "Partially Occupied"
                    )
                    output_file.write(f"{indices_banda[j]:<10} {energia_spin_down[j]:<14.6f} {ocupacion_spin_down[j]:<10.6f} {occupation_status}\n")
            break

# Analyze each block and save in eigenval_infos.dat file
with open(output_file_path, 'w') as output_file:
    for bloque_num, bloque in enumerate(blocks, start=1):
        analizar_bloque(bloque, bloque_num, output_file)

# Print the lists for spin up and spin down
print("Spin Up - Band index list:", band_index_list_up)
print("Spin Up - kpoint list:", kpoint_list_up)
print("Spin Up - Spin list:", spin_list_up)

print("Spin Down - Band index list:", band_index_list_down)
print("Spin Down - kpoint list:", kpoint_list_down)
print("Spin Down - Spin list:", spin_list_down)
print("##########################################################################################")
#print("The eigenval_infos.dat file has been saved.")





"Parsing the vasprun.xml file using the band_index_list_up, kpoint_list_up, spin_list_up, band_index_list_down, \
 kpoint_list_down lists and spin_list_down as inputs."
# Save the information from both spins in vasprun_infos.dat file
with open('vasprun_infos.dat', 'w') as file:
    # Spin up analysis
    if band_index_list_up and kpoint_list_up and spin_list_up:
        file.write("########################################################################\n")
        file.write("                               SPIN UP                                  \n")
        file.write("########################################################################\n")

        for i in range(len(band_index_list_up)):
            # Assign values from the band_index_list_up, kpoint_list_up, spin_list_up lists
            spin_number = spin_list_up[i]        # input
            kpoint_number = kpoint_list_up[i]    # input
            band_number = band_index_list_up[i]  # input

            # Load the vasprun.xml file
            # tree = ET.parse('vasprun.xml')
            # root = tree.getroot()

            # Find the spin up (1) superblock
            spin_set = root.find(f".//set[@comment='spin{spin_number}']")

            if spin_set is not None:
                # file.write(f"Information of superblock 'spin{spin_number}':\n")
                
                # Find the block corresponding to the kpoint
                kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']")
                
                if kpoint_block is not None:
                    file.write("########################################################################\n")
                    file.write(f"                               KPOINT {kpoint_number}                             \n")
                    file.write("########################################################################\n")
                    
                    # Find the subblock corresponding to the band
                    band_subblock = kpoint_block.find(f".//set[@comment='band {band_number}']")
                    
                    if band_subblock is not None:
                        file.write(f"Information of {band_subblock.attrib['comment']}:\n")
                        file.write(f"{'index':<6} {'s':<10} {'p':<10} {'d':<10} {'tot':<10}\n")
                        
                        # Print the subblock information with filter
                        for j, child in enumerate(band_subblock):
                            columns = child.text.split()
                            total_sum = sum(float(value) for value in columns)
                            # keep the complete decimals from vasprun.xml
#                            formatted_sum = f"{total_sum:.{len(columns[0].split('.')[-1])}f}"
                            
                            # set the decimals
                            formatted_values = [f"{float(value):.3f}" for value in columns]
                            formatted_sum = f"{total_sum:.3f}"
                            
                            # Only print if "tot" is greater than 0.1
                            if float(formatted_sum) > 0.1:
                                # keep the decimals from vasprun.xml
#                                file.write(f"{j + 1:<6} {columns[0]:<10} {columns[1]:<10} {columns[2]:<10} {formatted_sum:<10}\n")
                                # set the decimals
                                file.write(f"{j + 1:<6} {formatted_values[0]:<10} {formatted_values[1]:<10} {formatted_values[2]:<10} {formatted_sum:<10}\n")
                    else:
                        file.write(f"Subblock 'band {band_number}' not found in 'kpoint {kpoint_number}'.\n")
                else:
                    file.write(f"Block 'kpoint {kpoint_number}' not found in 'spin{spin_number}'.\n")
            else:
                file.write(f"Superblock 'spin{spin_number}' not found.\n")

    # Spin down analysis
    if band_index_list_down and kpoint_list_down and spin_list_down:
        file.write("\n\n\n")
        file.write("########################################################################\n")
        file.write("                               SPIN DOWN                                \n")
        file.write("########################################################################\n")

        for i in range(len(band_index_list_down)):
            # Assign values from the band_index_list_down, kpoint_list_down, spin_list_down lists
            spin_number = spin_list_down[i]
            kpoint_number = kpoint_list_down[i]
            band_number = band_index_list_down[i]

            # Load the vasprun.xml file
            # tree = ET.parse('vasprun.xml')
            # root = tree.getroot()

            # Find the spin down (2) superblock
            spin_set = root.find(f".//set[@comment='spin{spin_number}']")

            if spin_set is not None:
                # file.write(f"Information of superblock 'spin{spin_number}':\n")
                
                # Find the block corresponding to the kpoint
                kpoint_block = spin_set.find(f".//set[@comment='kpoint {kpoint_number}']")
                
                if kpoint_block is not None:
                    file.write("########################################################################\n")
                    file.write(f"                               KPOINT {kpoint_number}                             \n")
                    file.write("########################################################################\n")
                    
                    # Find the subblock corresponding to the band
                    band_subblock = kpoint_block.find(f".//set[@comment='band {band_number}']")
                    
                    if band_subblock is not None:
                        file.write(f"Information of {band_subblock.attrib['comment']}:\n")
                        file.write(f"{'index':<6} {'s':<10} {'p':<10} {'d':<10} {'tot':<10}\n")
                        
                        # Print the subblock information with filter
                        for j, child in enumerate(band_subblock):
                            columns = child.text.split()
                            total_sum = sum(float(value) for value in columns)
                            # keep the complete decimals from vasprun.xml
#                            formatted_sum = f"{total_sum:.{len(columns[0].split('.')[-1])}f}"
                            
                            # set the decimals
                            formatted_values = [f"{float(value):.3f}" for value in columns]
                            formatted_sum = f"{total_sum:.3f}"
                            
                            # Only print if "tot" is greater than 0.1
                            if float(formatted_sum) > 0.1:
                                # keep the decimals from vasprun.xml
#                                file.write(f"{j + 1:<6} {columns[0]:<10} {columns[1]:<10} {columns[2]:<10} {formatted_sum:<10}\n")
                                # set the decimals
                                file.write(f"{j + 1:<6} {formatted_values[0]:<10} {formatted_values[1]:<10} {formatted_values[2]:<10} {formatted_sum:<10}\n")
                    else:
                        file.write(f"Subblock 'band {band_number}' not found in 'kpoint {kpoint_number}'.\n")
                else:
                    file.write(f"Block 'kpoint {kpoint_number}' not found in 'spin{spin_number}'.\n")
            else:
                file.write(f"Superblock 'spin{spin_number}' not found.\n")

#print("The vasprun_infos.dat file has been saved.")


# Extract folder name from current directory
folder_name = os.path.basename(os.getcwd())
# Create 'localized' folder 
#localized_folder = f'../../../localized-defects/{folder_name}/'
localized_folder = 'localized-defects'
if not os.path.exists(localized_folder):
    os.makedirs(localized_folder)

    # Save the results
output_file = os.path.join(localized_folder, f'localized_{folder_name}.dat')

# Concatenate eigenval_infos.dat and vasprun_infos.dat
with open(output_file, 'w') as combined_file:
    # Read and write the content of eigenval_infos.dat
    combined_file.write(f"Defect: {folder_name}\n")
    combined_file.write(f"VBM = {VBM} eV\n")
    combined_file.write(f"CBM = {CBM} eV\n\n\n")
    combined_file.write("###########################################################\n")
    combined_file.write("                        EIGENVAL file                            \n")
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
        
print(f"The localized-defects/localized_{folder_name}.dat file has been created.")
