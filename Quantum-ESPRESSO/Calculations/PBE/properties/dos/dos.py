#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

import numpy as np
import matplotlib.pyplot as plt

VBM =   13.31233577

# Load data, skipping the first line (header)
data = np.loadtxt('diamond_dos.dat', comments='#')

# Rescale energy with respect to the VBM
energy = data[:, 0] - VBM

# DOS
dos = data[:, 1]

# Plot
plt.axvline(x=0, color='black', linestyle='--', linewidth=0.7)
plt.plot(energy, dos, color='xkcd:blue', linewidth=1)
plt.xlabel('Energy (eV)', fontsize=14)
plt.ylabel('DOS (States/eV)', fontsize=14)

plt.xlim(-22, 20)
plt.ylim(0, 2.8)

plt.tight_layout()
plt.savefig("diamond_dos.png", dpi=300)
