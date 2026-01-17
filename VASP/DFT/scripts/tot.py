#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

"Code for print the total energy from vaprun.xml files"
import sys
from pymatgen.io.vasp.outputs import Vasprun
import glob

def process_vasrun_file(filename):
    """Load a vasprun.xml file and return its total energy."""
    try:
        vasprun = Vasprun(filename)
        
        # Get the total energy from the last ionic step
        last_energy = vasprun.ionic_steps[-1]['electronic_steps'][-1]['e_fr_energy']
        
        return last_energy
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None  

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: test.py <pattern>")
        sys.exit(1)

    print(f"{'Filename':<20} {'Total energy (eV)':<20}")
    
    # Process each file passed as an argument
    for arg in sys.argv[1:]:
        files = glob.glob(arg)
        if not files:
            print(f"No files found for pattern: {arg}")
            continue
        
        for filename in files:
            total_energy = process_vasrun_file(filename)
            if total_energy is not None:
                # Print the filename and its total energy
                print(f"{filename:<20} {total_energy:<20.8f}")
