#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

import sys
import re

"Code for print the free energy TOTEN, energy without entropy (F) and energy(sigma->0) (E_0) from OUTCAR file"

def process_file(filename, print_header):
    if print_header:
        # Define column widths for alignment and print header 
        print(f"{'Filename':<20} {'Total energy (eV)':<20} {'F':<20} {'E_0':<20}", end="")
    
    with open(filename, 'r') as file:
        freeeV = None
        e0eV = None
        
        for line in file:
            if "free  energy" in line:
                match_free = re.search(r"(-*\d+\.\d+)", line)
                if match_free:
                    freeeV = match_free.group(1)

            elif "energy  without entropy" in line:
                match_e0 = re.search(r"(-*\d+\.\d+)\s+energy\(sigma-\>0\)\s+=\s+(-*\d+\.\d+)", line)
                if match_e0:
                    e0eV = match_e0.group(2)
                    if freeeV is not None:
                        # Print aligned values 
                        print(f"\n{filename:<20} {freeeV:<20} {freeeV:<20} {e0eV:<20}", end="")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: toten.py OUTCAR")
        sys.exit(1)

    # Process each file passed as an argument
    first_file = True

    for arg in sys.argv[1:]:
        process_file(arg, first_file)
        first_file = False  

    print()  

