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
    data = np.loadtxt(fname)
    energy = data[:, 0] - VBM
    pdos = data[:, 1]  # pdos col

    return energy, pdos

energy, pdos_s = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#1(s)")
_, pdos_p = data_loader(f"diamond_pdos.dat.pdos_atm#{atom}({element})_wfc#2(p)")

plt.plot(energy, pdos_s, linewidth=1, color='xkcd:green', label='s-orbital')
plt.plot(energy, pdos_p, linewidth=1, color='xkcd:blue', label='p-orbital')

plt.xlabel('Energy (eV)', fontsize=14)
plt.ylabel('DOS (States/eV)', fontsize=14)
plt.axvline(x=0, color='xkcd:black', linestyle='--', linewidth=0.75)
plt.xlim(-22, 20)
plt.ylim(0, 0.9)

plt.legend()
plt.tight_layout()
plt.savefig(rf"diamond_pdos-{element}-atom_{atom}-1.png", dpi=300)
