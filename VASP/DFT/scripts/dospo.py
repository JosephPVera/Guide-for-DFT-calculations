#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

"Plot the DOS using the OUTCAR and DOSCAR file"
"Usage:   dos.py 1 --s                             # plot the s-orbital for the atom 1 \
          dos.py 1 --p                             # plot the p-orbital for the atom 1 \
          dos.py 1 --d                             # plot the d-orbital for the atom 1 \
          dos.py 1 --all                           # plot the s,p,d-orbitals for the atom 1\
          dos.py 1 --tot --all                     # plot the total DOS and s,p,d-orbitals for the atom 1 \
          dos.py --tot                             # plot the total DOS \
          dos.py 1 --s --x -10 20 --y 0 10         # introduce the y range \
          dos.py 1 --tot --all --x -10 20 --y 0 10 # introduce the x range"  

import numpy as np
import matplotlib.pyplot as plt
import re
import sys

def get_value_from_outcar(key, outcar_file="OUTCAR"):
    "Extract specific values (NEDOS, ISPIN and E-fermi) from the OUTCAR file"
    patterns = {
        "NEDOS": r'number of dos\s+NEDOS\s*=\s*(\d+)',
        "ISPIN": r'ISPIN\s*=\s*(\d+)',
        "E-fermi": r'E-fermi\s*:\s*([-\d.]+)'
    }
    pattern = patterns.get(key)
    if not pattern:
        return None

    with open(outcar_file, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                return int(match.group(1)) if key in ["NEDOS", "ISPIN"] else float(match.group(1))
    return None

NEDOS = get_value_from_outcar("NEDOS")
ISPIN = get_value_from_outcar("ISPIN")
fermi_energy = get_value_from_outcar("E-fermi")

# Parse additional axis range arguments
x_min, x_max = None, None
y_min, y_max = None, None
for i, arg in enumerate(sys.argv):
    if arg == '--x' and i + 2 < len(sys.argv):
        x_min, x_max = float(sys.argv[i + 1]), float(sys.argv[i + 2])
    elif arg == '--y' and i + 2 < len(sys.argv):
        y_min, y_max = float(sys.argv[i + 1]), float(sys.argv[i + 2])

def plot_dos_total():
    "Plot total DOS"
    fig, ax = plt.subplots(figsize=(12, 8))
    if ISPIN == 1:
        dos_data = np.loadtxt("DOSCAR", unpack=True, usecols=(0, 1), skiprows=6, max_rows=NEDOS)
        energies = dos_data[0] - fermi_energy  
        spin_up = dos_data[1]          
        ax.plot(energies, spin_up, linestyle='-', color='r', label='Total DOS')   
        ax.fill_between(energies, spin_up, alpha=0.1, color='r') # Fill between the curve and the x-axis
        
    elif ISPIN == 2:
        dos_data = np.loadtxt("DOSCAR", unpack=True, usecols=(0, 1, 2), skiprows=6, max_rows=NEDOS)
        energies = dos_data[0] - fermi_energy
        spin_up = dos_data[1]
        spin_down = dos_data[2] * -1
        ax.plot(energies, spin_up, linestyle='-', color='r', label='Total DOS')
        ax.plot(energies, spin_down, linestyle='-', color='r', label=None)#, label='Spin down')
        ax.fill_between(energies, spin_up, alpha=0.1, color='r')  # Fill for spin up
        ax.fill_between(energies, spin_down, alpha=0.1, color='r') # Fill for spin down (optional)
        
    ax.axvline(x=0, color='k', linestyle='dashed', linewidth = 1)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.9)
    ax.set_ylabel('DOS (States/eV)', fontsize = 14)
    ax.set_xlabel('Energy (eV)', fontsize = 14)
    ax.legend()
    
    # Set axis ranges if specified
    if x_min is not None and x_max is not None:
        ax.set_xlim(x_min, x_max)
    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)

    plt.savefig("total_dos.png", dpi=300, bbox_inches='tight')  
    plt.show()

def plot_dos_for_atom(atom_number, orbital_types=None):
    "Plot DOS for a specific atom and orbitals"
    "data[1]: s-orbital (spin up), data[2]: s-orbital (spin down) \
    data[3]: p_x-orbital (spin up), data[5]: p_y-orbital (spin up), data[7]: p_z-orbital (spin up), \
    data[4]: p_x-orbital (spin down), data[6]: p_y-orbital (spin down), data[8]: p_z-orbital (spin down), \
    data[9]: d_xy-orbital (spin up), data[11]: d_yz-orbital (spin up), data[13]: d_xz-orbital (spin up), data[15]: d_{x²-y²}-orbital (spin up), data[17]: d_z²-orbital (spin up), \
    data[10]: d_xy-orbital (spin down), data[12]: d_yz-orbital (spin down), data[14]: d_xz-orbital (spin down), data[16]: d_{x²-y²}-orbital (spin dow), data[18]: d_z²-orbital (spin down)"    
    start_line = NEDOS + 8 + (atom_number - 1) * (NEDOS + 1)
    data = np.loadtxt("DOSCAR", unpack=True, skiprows=start_line - 1, max_rows=NEDOS)

    energies = data[0] - fermi_energy
    
    fig, ax = plt.subplots(figsize=(12, 8))
    def plot_dos(x, y, color, label):
        ax.plot(x, y, linestyle='-', markersize=1, color=color, label=label)
        
    if orbital_types is None:
        orbital_types = ['s', 'p', 'd']

    if ISPIN == 1:
        if 's' in orbital_types:
            s_orbital_up = data[1]
            plot_dos(energies, s_orbital_up, 'g', label='s-orbital')
            ax.fill_between(energies, s_orbital_up, alpha= 0.1, color='g')  # Fill under s-orbital
        if 'p' in orbital_types:
            p_orbital_up = data[2] + data[3] + data[4]
            plot_dos(energies, p_orbital_up, 'b', label='p-orbital')
            ax.fill_between(energies, p_orbital_up, alpha= 0.1, color='b')  # Fill under p-orbital
        if 'd' in orbital_types:
            d_orbital_up = data[5] + data[6] + data[7] + data[8] + data[9]
            plot_dos(energies, d_orbital_up, 'r', label='d-orbital')
            ax.fill_between(energies, d_orbital_up, alpha= 0.1, color='r')  # Fill under d-orbital

    elif ISPIN == 2:
        if 's' in orbital_types:
            s_orbital_up = data[1]
            s_orbital_down = data[2]
            plot_dos(energies, s_orbital_up, 'g', label='s-orbital')
            plot_dos(energies, s_orbital_down * -1, 'g', label=None)
            ax.fill_between(energies, s_orbital_up, alpha=0.1, color='g')  # Fill under s-orbital up
            ax.fill_between(energies, s_orbital_down * -1, alpha=0.1, color='g')  # Fill under s-orbital down
        if 'p' in orbital_types:
            p_orbital_up = data[3] + data[5] + data[7]
            p_orbital_down = (data[4] + data[6] + data[8]) * -1
            plot_dos(energies, p_orbital_up, 'b', label='p-orbital')
            plot_dos(energies, p_orbital_down, 'b', label=None)
            ax.fill_between(energies, p_orbital_up, alpha=0.1, color='b')  # Fill under p-orbital up
            ax.fill_between(energies, p_orbital_down, alpha=0.1, color='b')  # Fill under p-orbital down
        if 'd' in orbital_types:
            d_orbital_up = data[9] + data[11] + data[13] + data[15] + data[17]
            d_orbital_down = (data[10] + data[12] + data[14] + data[16] + data[18]) * -1
            plot_dos(energies, d_orbital_up, 'r', label='d-orbital')
            plot_dos(energies, d_orbital_down, 'r', label=None)
            ax.fill_between(energies, d_orbital_up, alpha=0.1, color='r')  # Fill under d-orbital up
            ax.fill_between(energies, d_orbital_down, alpha=0.1, color='r')  # Fill under d-orbital down

    ax.axvline(x=0, color='k', linestyle='dashed', linewidth = 1)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.9)
    ax.set_ylabel('DOS (States/eV)', fontsize = 14)
    ax.set_xlabel('Energy (eV)', fontsize = 14)
    ax.legend()

    # Set axis ranges if specified
    if x_min is not None and x_max is not None:
        ax.set_xlim(x_min, x_max)
    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)
              
    if '--s' in sys.argv or '--p' in sys.argv or '--d' in sys.argv:
        plt.savefig(f"atom_{atom_number}-{orbital_types}_orbital-LDOS.png", dpi=200, bbox_inches='tight')
    else:
        plt.savefig(f"atom_{atom_number}-LDOS.png", dpi=200, bbox_inches='tight')
    plt.show()

def plot_dos_combined(atom_number, orbital_types=None):
    "Plot total DOS and orbitals for a specific atom."
    fig, ax = plt.subplots(figsize=(12, 8))

    if ISPIN == 1:
        dos_data = np.loadtxt("DOSCAR", unpack=True, usecols=(0, 1), skiprows=6, max_rows=NEDOS)
        energies = dos_data[0] - fermi_energy  
        spin_up = dos_data[1]          
        ax.plot(energies, spin_up, linestyle='-', color='r', label='Total DOS')   
        ax.fill_between(energies, spin_up, alpha=0.1, color='r') # Fill between the curve and the x-axis
        
    elif ISPIN == 2:
        dos_data = np.loadtxt("DOSCAR", unpack=True, usecols=(0, 1, 2), skiprows=6, max_rows=NEDOS)
        energies = dos_data[0] - fermi_energy
        spin_up = dos_data[1]
        spin_down = dos_data[2] * -1  # Invert spin down for plotting
        ax.plot(energies, spin_up, linestyle='-', color='r', label='Total DOS')
        ax.plot(energies, spin_down, linestyle='-', color='r', label=None)# label='Spin down')
        ax.fill_between(energies, spin_up, alpha=0.1, color='r')  # Fill for spin up
        ax.fill_between(energies, spin_down, alpha=0.1, color='r') # Fill for spin down (optional)
            
    # Now plot DOS for the specific atom
    start_line = NEDOS + 8 + (atom_number - 1) * (NEDOS + 1)
    data = np.loadtxt("DOSCAR", unpack=True, skiprows=start_line - 1, max_rows=NEDOS)
    energies = data[0] - fermi_energy
    
    def plot_dos(x, y, color, label):
        ax.plot(x, y, linestyle='-', markersize=1, color=color, label=label)

    if orbital_types is None:
        orbital_types = ['s', 'p', 'd']  # Default to all orbitals

    if ISPIN == 1:
        # Plotting s-orbital
        if 's' in orbital_types:
            s_orbital_up = data[1]
            plot_dos(energies, s_orbital_up, 'g', label='s-orbital')#f's-orbital (Spin up) Atom {atom_number}')  
            ax.fill_between(energies, s_orbital_up, alpha= 0.1, color='g')  # Fill under s-orbital

        # Plotting p-orbital 
        if 'p' in orbital_types:
            p_orbital_up = data[2] + data[3] + data[4]  
            plot_dos(energies, p_orbital_up, 'b', label='p-orbital')#f'p-orbital (Spin up) Atom {atom_number}')
            ax.fill_between(energies, p_orbital_up, alpha= 0.1, color='b')  # Fill under p-orbital

        # Plotting d-orbital 
        if 'd' in orbital_types:
            d_orbital_up = (data[5] + data[6] + data[7] + data[8] + data[9])
            plot_dos(energies, d_orbital_up, 'r', label='d-orbital')# f'd-orbital (Spin up) Atom {atom_number}')
            ax.fill_between(energies, d_orbital_up, alpha= 0.1, color='r')  # Fill under d-orbital

    elif ISPIN == 2:
        # Plotting s-orbital 
        if 's' in orbital_types:
            s_orbital_up = data[1]
            s_orbital_down = data[2]
            plot_dos(energies, s_orbital_up, 'g', label='s-orbital')#f's-orbital (Spin up) Atom {atom_number}')             
            plot_dos(energies, s_orbital_down * -1, 'g', label=None)#, label=f's-orbital (Spin down) Atom {atom_number}')
            ax.fill_between(energies, s_orbital_up, alpha=0.1, color='g')  # Fill under s-orbital up
            ax.fill_between(energies, s_orbital_down * -1, alpha=0.1, color='g')  # Fill under s-orbital down

        # Plotting p-orbital 
        if 'p' in orbital_types:
            p_orbital_up = data[3] + data[5] + data[7]  
            p_orbital_down = (data[4] + data[6] + data[8]) * -1 
            plot_dos(energies, p_orbital_up, 'b', label='p-orbital')#f'p-orbital (Spin up) Atom {atom_number}')
            plot_dos(energies, p_orbital_down, 'b', label=None)#, f'p-orbital (Spin down) Atom {atom_number}')
            ax.fill_between(energies, p_orbital_up, alpha=0.1, color='b')  # Fill under p-orbital up
            ax.fill_between(energies, p_orbital_down, alpha=0.1, color='b')  # Fill under p-orbital down

        # Plotting d-orbital 
        if 'd' in orbital_types:
            d_orbital_up = (data[9] + data[11] + data[13] + data[15] + data[17])
            d_orbital_down = ((data[10] + data[12] + data[14] + data[16] + data[18]) * -1)
            plot_dos(energies, d_orbital_up, 'r', label='d-orbital')# f'd-orbital (Spin up) Atom {atom_number}')
            plot_dos(energies, d_orbital_down, 'r', label=None)#, f'd-orbital (Spin down) Atom {atom_number}')    
            ax.fill_between(energies, d_orbital_up, alpha=0.1, color='r')  # Fill under d-orbital up
            ax.fill_between(energies, d_orbital_down, alpha=0.1, color='r')  # Fill under d-orbital down
    
    ax.axvline(x=0, color='k', linestyle='dashed', linewidth = 1)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.9)
    ax.set_ylabel('DOS (States/eV)', fontsize = 14)
    ax.set_xlabel('Energy (eV)', fontsize = 14)
    ax.legend()

    # Set axis ranges if specified
    if x_min is not None and x_max is not None:
        ax.set_xlim(x_min, x_max)
    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)

    plt.savefig(f"atom_{atom_number}-TDOS-orbitals.png", dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    # Initialize variables
    atom_number = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    orbital_types = []
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: dos.py atom_number --s/--p/--d/--all or dos.py --tot or dos.py atom_number --all --tot")
        sys.exit(1)

    # Parse arguments
    if '--tot' in sys.argv:
        if '--all' in sys.argv:
            atom_number = int(sys.argv[1]) 
            plot_dos_combined(atom_number)
        else:
            plot_dos_total()
    else:
        atom_number = int(sys.argv[1])
        if '--s' in sys.argv:
            plot_dos_for_atom(atom_number, orbital_types='s')
        elif '--p' in sys.argv:
            plot_dos_for_atom(atom_number, orbital_types='p')
        elif '--d' in sys.argv:
            plot_dos_for_atom(atom_number, orbital_types='d')
        elif '--all' in sys.argv:
            plot_dos_for_atom(atom_number, orbital_types=['s', 'p', 'd'])
