#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

import numpy as np
import argparse

def compute_nk_values(poscar_file, kdensity=4.0):
    k_dist = 1 / kdensity

    with open(poscar_file, 'r') as file:
        lines = file.readlines()
        
        # vectors
        a_1 = list(map(float, lines[2].split()))  
        a_2 = list(map(float, lines[3].split()))  
        a_3 = list(map(float, lines[4].split())) 
    
    # lattice parameters
    a = np.sqrt(a_1[0]**2 + a_1[1]**2 + a_1[2]**2)
    b = np.sqrt(a_2[0]**2 + a_2[1]**2 + a_2[2]**2)
    c = np.sqrt(a_3[0]**2 + a_3[1]**2 + a_3[2]**2)
    
    # Calculate n_k and round to the nearest integer (kpoints mesh)
    n_k_1 = int(np.ceil((2*np.pi) / (a*k_dist)))
    n_k_2 = int(np.ceil((2*np.pi) / (b*k_dist)))
    n_k_3 = int(np.ceil((2*np.pi) / (c*k_dist)))
    
    return n_k_1, n_k_2, n_k_3, kdensity

def kpoints_file(n_k_1, n_k_2, n_k_3, kdensity, filename="KPOINTS"):
    with open(filename, 'w') as file:
        file.write(f"k-density: {kdensity:.1f}\n")
        file.write("0\n")
        file.write("Gamma\n")
        file.write(f" {n_k_1:1d} {n_k_2:2d} {n_k_3:2d}\n")  
        file.write(" 0  0  0\n")

parser = argparse.ArgumentParser(description="Generate a KPOINTS file with specified k-density.")
parser.add_argument("--d", type=float, default=4.0, help="Specify the k-density value. Default is 4.0.")
args = parser.parse_args()

poscar_file = 'POSCAR'

# Compute and write the KPOINTS file
n_k_1, n_k_2, n_k_3, kdensity = compute_nk_values(poscar_file, args.d)
kpoints_file(n_k_1, n_k_2, n_k_3, kdensity)

print(f"k-density: {kdensity}")
print(f"k-point mesh: {n_k_1}x{n_k_2}x{n_k_3}")
