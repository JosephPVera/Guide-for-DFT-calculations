#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-07

import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('diamond_bands.dat.gnu')

k = np.unique(data[:, 0])
bands1 = np.reshape(data[:, 1], (-1, len(k)))

VBM = 13.31233577

# Rescale energy with respect to the VBM
bands = bands1 - VBM

for band in range(len(bands)):
    plt.plot(k, bands[band, :], linewidth=1, color='xkcd:blue')
plt.xlim(min(k), max(k))
 
Gap = 4.09639783
plt.axhline(0, linestyle='--', linewidth=0.75, color='xkcd:black')
plt.axhline(Gap, linestyle='--', linewidth=0.75, color='xkcd:black')

# High symmetry k-points
r = 0.0
X = 0.70710678
W = 1.06066017
K = 1.31066017
r1 = 2.06066017
L = 2.67303261
U = 3.10604531
W1 = 3.35604531
L1 = 3.85604531
K1 = 4.28905801

plt.axvline(X, linewidth=0.2, color='xkcd:black')
plt.axvline(W, linewidth=0.2, color='xkcd:black')
plt.axvline(K, linewidth=0.2, color='xkcd:black')
plt.axvline(r1, linewidth=0.2, color='xkcd:black')
plt.axvline(L, linewidth=0.2, color='xkcd:black')
plt.axvline(U, linewidth=0.2, color='xkcd:black')
plt.axvline(W1, linewidth=0.2, color='xkcd:black')
plt.axvline(L1, linewidth=0.2, color='xkcd:black')
plt.axvline(K1, linewidth=0.2, color='xkcd:black')

# High symmetry points
plt.xticks(ticks= [r, X, W, K, r1, L, U, W1, L1, K1], labels=[r'$\Gamma$', 'X', 'W', 'K', r'$\Gamma$', 'L', 'U', 'W', 'L', 'K' ], fontsize=12)

plt.ylabel('Energy (eV)', fontsize=14)
plt.ylim(-10, 15)

plt.tight_layout()
plt.savefig("diamond_bands.png", dpi=200, bbox_inches='tight')
