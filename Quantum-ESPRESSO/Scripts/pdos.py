#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-07

import matplotlib.pyplot as plt
from matplotlib import rcParamsDefault
import numpy as np

VBM = 13.31233577

atom = 2
element = "C"

def data_loader(fname):
    data = np.loadtxt(fname)
    energy = data[:, 0] - VBM
    pdos_cols = [data[:, i] for i in range(2, data.shape[1])] 
    
    return energy, pdos_cols

# s-orbital: 1 column
energy, (pdos_s,) = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#1(s)")

# p-orbital: 3 columns (pz, px, py)
_, (pdos_pz, pdos_px, pdos_py) = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#2(p)")

plt.plot(energy, pdos_s, linewidth=1, color='xkcd:green', label='s-orbital')
plt.plot(energy, pdos_px, linewidth=1, color='xkcd:blue', label=r'p$_{x}$-orbital')
plt.plot(energy, pdos_py, linewidth=1, color='xkcd:red', label=r'p$_{y}$-orbital')
plt.plot(energy, pdos_pz, linewidth=1, color='xkcd:purple', label=r'p$_{z}$-orbital')

plt.xlabel('Energy (eV)', fontsize=14)
plt.ylabel('DOS (States/eV)', fontsize=14)
plt.axvline(x=0, color='xkcd:black', linestyle='--', linewidth=0.75)
plt.xlim(-22, 20)
plt.ylim(0, 0.6)

plt.legend()
plt.tight_layout()
plt.savefig(rf"diamond_pdos-{element}-atom_{atom}.png", dpi=300)
