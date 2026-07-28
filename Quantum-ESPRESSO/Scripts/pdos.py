#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-07

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
    pdos = data[:, 1]  # pdos col, total contribution for a given orbital

    return energy, pdos

energy, pdos_s = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#1(s)")
_, pdos_p = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#2(p)")
#_, pdos_tot = data_loader('diamond_pdos.dat.pdos_tot')

# make plots
plt.plot(energy, pdos_s, linewidth=1, color='xkcd:green', label='s-orbital')
plt.plot(energy, pdos_p, linewidth=1, color='xkcd:blue', label='p-orbital')
#plt.plot(energy, pdos_tot, linewidth=0.75, color='k', label='total')

plt.xlabel('Energy (eV)', fontsize=14)
plt.ylabel('DOS (States/eV)', fontsize=14)
plt.axvline(x=0, color='xkcd:black', linestyle='--', linewidth=0.75)
plt.xlim(-22, 20)
plt.ylim(0, 0.9)

plt.legend()
plt.tight_layout()
plt.savefig(rf"diamond_pdos-{element}-atom_{atom}.png", dpi=300)
