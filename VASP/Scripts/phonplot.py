#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

import matplotlib.pyplot as plt
import re
import argparse
import pandas as pd
import numpy as np

"Code for plot DOS, PDOS, thermal properties and band structure using the outputs from phonopy calculations."
"The output are saved with the following names: DOS  ----> total_dos.dat \
                                                PDOS ----> projected_dos.dat \
                                                Thermal ----> thermal.dat \
                                                Single Band ----> band.dat \
                                                Merge Band with and without NAC ----> band_nac.dat and band_nonac.dat"
                                                
"Usage: ----> phonplot.py --tdos                    # Total DOS \
        ----> phonplot.py --pdos                    # Partial DOS \
        ----> phonplot.py --ter                     # Thermal properties \
        ----> phonplot.py --band                    # Band structure \
        ----> phonplot.py --tband                   # band structure with and without NAC \
        ----> phonplot.py --tdos --x 0 12 --y -1 23 # Total DOS, set y and x-axis range"


def get_atomic_symbols(conf_file='band.conf'): 
    symbols = []
    with open(conf_file, 'r') as file:
        for line in file:
            if 'ATOM_NAME' in line:
                # Split the line and extract symbols
                parts = line.split('=')
                if len(parts) > 1:
                    # Get the part after the '=' and strip any whitespace
                    symbols = parts[1].strip().split()
                break
    return symbols
        
def plot_total_dos(file_path='total_dos.dat', x_range=None, y_range=None):
    data = []
    with open(file_path, 'r') as file:
        next(file)  # Skip the first line
        for line in file:
            columns = line.split()
            if len(columns) >= 2: 
                data.append((float(columns[0]), float(columns[1])))
    
    # Separate the columns into x and y lists
    x, y = zip(*data)
    
    plt.figure(figsize=(12, 8))
    plt.plot(x, y, label="Total DOS", color='r')
    plt.fill_between(x, y, alpha=0.1, color='r')
    plt.xlabel('Frequency (THz)', fontsize=14)
    plt.ylabel('DOS (States/eV)', fontsize=14)

    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.legend()
    plt.tight_layout()
    plt.savefig('tdos.png', dpi=150)
    plt.show()
    plt.close()

def plot_pdos(file_path='projected_dos.dat', x_range=None, y_range=None):
    data = []
    with open(file_path, 'r') as file:
        next(file)  # Skip the first line
        for line in file:
            columns = line.split()
            if len(columns) >= 3: 
                data.append((float(columns[0]), float(columns[1]), float(columns[2])))
    
    # Separate the columns into x, y1, and y2 lists
    x, y1, y2 = zip(*data)

    symbols = get_atomic_symbols()

    plt.figure(figsize=(12, 8))
    plt.plot(x, y1, label=symbols[0], color="green")
    plt.plot(x, y2, label=symbols[1], color="orange")
    plt.fill_between(x, y1, alpha=0.1, color="green")
    plt.fill_between(x, y2, alpha=0.1, color="orange")
    
    plt.xlabel('Frequency (THz)', fontsize=14)
    plt.ylabel('PDOS (States/eV)', fontsize=14)

    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.legend()
    plt.tight_layout()
    plt.savefig('pdos.png', dpi=150)
    plt.show()
    plt.close()

def plot_thermal(file_path='thermal.dat', x_range=None, y_range=None):
    custom_labels = ['Helmholtz Free energy (kJ/mol)', 'Entropy (J/K.mol)', 'Heat Capacity $C_{v}$ (J/K.mol)', 'Energy (kJ/mol)']
    with open(file_path, 'r') as file:
        lines = file.readlines()[0:]  # Skip 

    # Filter lines containing numbers and convert to DataFrame
    valid_lines = [line for line in lines if all(part.replace('.', '', 1).isdigit() for part in line.split())]
    
    data = pd.DataFrame(
        [line.split() for line in valid_lines],  # Split each line into columns
        dtype=float  # Convert all values to floats
    )
    
    x_column = data[0]  
    y_columns = [1, 2, 3, 4]  

    colors = ['g', 'orange', 'b', 'r'] 
    
    plt.figure(figsize=(12, 8))
    
    for i, (y_col, label) in enumerate(zip(y_columns, custom_labels)):
        plt.plot(x_column, data[y_col], label=label, color=colors[i % len(colors)]) 

    plt.xlim(x_column.min(), x_column.max())
    plt.xlabel('Temperatura (K)', fontsize = 14)
    
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.legend()
    plt.tight_layout()
    plt.savefig('thermal_properties.png',dpi=150)
    plt.show()
    plt.close()

def get_band_labels(config_file='band.conf'):
    band_labels = []
    with open(config_file, 'r') as file:
        for line in file:
            if "BAND_LABELS" in line:
                label_string = line.split('=')[1]
                
                label_string = label_string.replace('\\Gamma', '$\\Gamma$')

                #  A:B format or singles
                parts = re.findall(r'\$\\Gamma\$|[A-Za-z]+(?::[A-Za-z]+)?', label_string)

                for part in parts:
                    if ':' in part:
                        left, right = part.split(':')
                        band_labels.append(f'{left}|{right}')
                    else:
                        band_labels.append(part)
                break
    return band_labels

def plot_blocks(data, ax, color, label):
    is_block_start = np.concatenate(([True], np.diff(data[:, 0]) < 0))
    block_indices = np.where(is_block_start)[0]

    for i in range(len(block_indices)):
        if i < len(block_indices) - 1:
            block_data = data[block_indices[i]:block_indices[i + 1]]
        else:
            block_data = data[block_indices[i]:]  # Last block

        ax.plot(block_data[:, 0], block_data[:, 1], linestyle='-', markersize=1, c=color, label=label if i == 0 else "")
        
def plot_single_band(nac_file="band.dat", color_nac='r', x_range=None, y_range=None):
    # Load k_path data from the second line in the band.dat file
    with open(nac_file, 'r') as file:
        file.readline()  # Skip the first line
        k_path_line = file.readline().strip()
    k_path = list(map(float, k_path_line[1:].split()))  # Convert to float

    # Load the data (skip header lines)
    data = np.loadtxt(nac_file, comments='#', skiprows=2)

    fig, ax = plt.subplots()
    
    band_labels = get_band_labels()

    # Plot data
    plot_blocks(data, ax, color_nac, 'Without NAC')

    # Add vertical lines at specified k-path positions
    for x in k_path[1:-1]:
        ax.axvline(x=x, color='k', linestyle='-', linewidth=0.9)

    ax.set_ylabel('Frequency (THz)', fontsize=14)
    fig.set_size_inches(12, 8)
    plt.xlim(0.0, k_path[-1])
    plt.axhline(y=0.00, color='k', linestyle='dashed')

    # Set custom tick labels: BAND_LABELS and k_path
    ax.set_xticks(k_path)
    ax.set_xticklabels(band_labels)

    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('band.png', dpi=150)
    plt.show()
    plt.close()

def plot_mix_band(nac_file="band_nac.dat", no_nac_file="band_nonac.dat", color_nac='xkcd:red', color_no_nac='xkcd:blue', x_range=None, y_range=None):
    # Load k_path data from the second line in the band.dat file
    with open(nac_file, 'r') as file:
        file.readline()  # Skip the first line
        k_path_line = file.readline().strip()
    k_path = list(map(float, k_path_line[1:].split()))  # Convert to float

    # Load data for NAC and without NAC (skip header lines)
    data_nac = np.loadtxt(nac_file, comments='#', skiprows=2)
    data_no_nac = np.loadtxt(no_nac_file, comments='#', skiprows=2)

    fig, ax = plt.subplots()
    
    band_labels = get_band_labels()

    # Plot data with NAC
    plot_blocks(data_nac, ax, color_nac, 'With NAC')
    # Plot data without NAC
    plot_blocks(data_no_nac, ax, color_no_nac, 'Without NAC')

    # Add vertical lines at specified k-path positions
    for x in k_path[1:-1]:
        ax.axvline(x=x, color='xkcd:black', linestyle='-', linewidth=0.2)

    ax.set_ylabel('Frequency (THz)', fontsize=16)
    fig.set_size_inches(12, 8)
    plt.xlim(0.0, k_path[-1])
    plt.axhline(y=0.00, color='xkcd:black', linestyle='dashed', linewidth=1)

    # Set custom tick labels: BAND_LABELS and k_path
    ax.set_xticks(k_path)
    ax.set_xticklabels(band_labels, fontsize=14)

    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('band_combinate.png', dpi=150)
    plt.show()
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Plotting functions for phonon data.')
    
    parser.add_argument('--tdos', action='store_true', help='Plot total DOS.')
    parser.add_argument('--pdos', action='store_true', help='Plot projected DOS.')
    parser.add_argument('--ter', action='store_true', help='Plot thermal non-adiabatic results.')
    parser.add_argument('--band', action='store_true', help='Plot single band structure.')
    parser.add_argument('--tband', action='store_true', help='Plot mixed band structure.')
    
    parser.add_argument('--x', nargs=2, type=float, help='Set x-axis range as two values: min max')
    parser.add_argument('--y', nargs=2, type=float, help='Set y-axis range as two values: min max')
    
    args = parser.parse_args()
    
    x_range = (args.x[0], args.x[1]) if args.x else None
    y_range = (args.y[0], args.y[1]) if args.y else None

    if args.tdos:
        plot_total_dos(x_range=x_range, y_range=y_range)
    elif args.pdos:
        plot_pdos(x_range=x_range, y_range=y_range)
    elif args.ter:
        plot_thermal(x_range=x_range, y_range=y_range)
    elif args.band:
        plot_single_band(x_range=x_range, y_range=y_range)
    elif args.tband:
        plot_mix_band(x_range=x_range, y_range=y_range)
    else:
        print("No valid argument provided. Please specify one of the following options:")
        print("--tdos, --pdos, --ter, --band, --tband")

if __name__ == '__main__':
    main()
