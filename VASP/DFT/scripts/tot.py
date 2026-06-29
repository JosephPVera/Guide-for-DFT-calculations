#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

"Code for print the total energy from vaprun.xml files"
import os
import re
from collections import defaultdict

def process_vasrun_file(filename):
    last_value = None
    pattern = re.compile(r'<i name="e_wo_entrp">\s*([-+]?\d*\.\d+)\s*</i>')
    
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                last_value = match.group(1)  # Update last occurrence
    
    return last_value  # Return the extracted energy

if __name__ == "__main__":
    base_directory = os.getcwd()  # Use current directory as the base
    
    results = []
    
    for root, _, files in os.walk(base_directory):
        if 'vasprun.xml' in files:
            vasprun_path = os.path.join(root, 'vasprun.xml')
            total_energy = process_vasrun_file(vasprun_path)
            folder_name = os.path.basename(root)  # Extract folder name
            
            results.append((folder_name, total_energy))

    # Grouping folders with similar prefixes
    grouped_results = defaultdict(list)
    for folder, total_energy in results:
        prefix = ''.join([char for char in folder if char.isalpha()])  # Extract alphabetic prefix
        grouped_results[prefix].append((folder, total_energy))

    # Print Folder and Total Energy
    print(f"{'Folder':<15} {'Total energy (eV)':<20}")
    for entries in grouped_results.values():
        print("-" * 34)
        for folder_name, total_energy in entries:
            if total_energy is not None:
                print(f"{folder_name:<15} {float(total_energy):<20.6f}")
            else:
                print(f"{folder_name:<15} {'Value not found':<20}")
