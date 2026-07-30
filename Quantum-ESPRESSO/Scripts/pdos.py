#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

import matplotlib.pyplot as plt
from matplotlib import rcParamsDefault
import numpy as np

VBM = 13.31233577

atom = 2
element = "C"

# load data
def data_loader(fname):
    data = np.loadtxt(fname)
    energy = data[:, 0] - VBM
    pdos_cols = [data[:, i] for i in range(2, data.shape[1])] 
    
    return energy, pdos_cols

# s-orbital: 1 column (m=0)
energy, (pdos_s,) = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#1(s)")

# p-orbital: 3 columns (pz, px, py)
_, (pdos_pz, pdos_px, pdos_py) = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#2(p)")

plt.plot(energy, pdos_s, linewidth=1, color='xkcd:green', label='s-orbital')
plt.plot(energy, pdos_px, linewidth=1, color='xkcd:blue', label=r'p$_{x}$-orbital')
plt.plot(energy, pdos_py, linewidth=1, color='xkcd:red', label=r'p$_{y}$-orbital')
plt.plot(energy, pdos_pz, linewidth=1, color='xkcd:purple', label=r'p$_{z}$-orbital')

#plt.yticks([])
plt.xlabel('Energy (eV)', fontsize=14)
plt.ylabel('DOS (States/eV)', fontsize=14)
plt.axvline(x=0, color='xkcd:black', linestyle='--', linewidth=0.75)
plt.xlim(-22, 20)
plt.ylim(0, 0.6)

#plt.fill_between(energy, 0, pdos_s, where=(energy < 0), facecolor='#006699', alpha=0.25)
#plt.fill_between(energy, 0, pdos_p, where=(energy < 0), facecolor='r', alpha=0.25)
#plt.fill_between(energy, 0, pdos_tot, where=(energy < 0), facecolor='k', alpha=0.25)
# plt.text(6.5, 0.52, 'Fermi energy', fontsize= small, rotation=90)

plt.legend()#frameon=False)
plt.tight_layout()
plt.savefig(rf"diamond_pdos-{element}-atom_{atom}.png", dpi=300)
