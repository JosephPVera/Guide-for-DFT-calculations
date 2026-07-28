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
    import numpy as np

    data = np.loadtxt(fname)
    energy = data[:, 0] - VBM
    pdos = data[:, 1]  # ldos col, total contribution for a given orbital

    return energy, pdos

energy, pdos_s = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#1(s)")
_, pdos_p = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#2(p)")
#_, pdos_tot = data_loader('graphene_pdos.dat.pdos_tot')

# make plots
#plt.figure(figsize = (8, 4))
plt.plot(energy, pdos_s, linewidth=1, color='xkcd:green', label='s-orbital')
plt.plot(energy, pdos_p, linewidth=1, color='xkcd:blue', label='p-orbital')
#plt.plot(energy, pdos_tot, linewidth=0.75, color='k', label='total')

#plt.yticks([])
plt.xlabel('Energy (eV)', fontsize=14)
plt.ylabel('DOS (States/eV)', fontsize=14)
plt.axvline(x=0, color='xkcd:black', linestyle='--', linewidth=0.75)
plt.xlim(-22, 20)
plt.ylim(0, 0.9)

#plt.fill_between(energy, 0, pdos_s, where=(energy < 0), facecolor='#006699', alpha=0.25)
#plt.fill_between(energy, 0, pdos_p, where=(energy < 0), facecolor='r', alpha=0.25)
#plt.fill_between(energy, 0, pdos_tot, where=(energy < 0), facecolor='k', alpha=0.25)
# plt.text(6.5, 0.52, 'Fermi energy', fontsize= small, rotation=90)

plt.legend()#frameon=False)
plt.tight_layout()
plt.savefig(rf"diamond_pdos-{element}-atom_{atom}.png", dpi=300)
