#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

import os

name = 'diamond_scf'

# base cell (angstrom)
base_cell = [
    (-1.786102785,  0.000000000,  1.786102785),
    (-0.000000000,  1.786102785,  1.786102785),
    (-1.786102785,  1.786102785,  0.000000000),
]

scale_factors = [0.94, 0.95, 0.96, 0.97, 0.98, 0.99,
                  1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06]

outdir = "cells"

# QE (scf) input template
TEMPLATE = """&CONTROL
  calculation = 'scf',
  prefix      = 'diamond-HSE06',
  outdir      = './tmp/',
  pseudo_dir  = '../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  restart_mode = 'from_scratch',
  disk_io = 'nowf',
/

&SYSTEM
  ibrav =  0,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  nbnd = 8,
  input_dft='hse',
  exx_fraction = 0.25,
  screening_parameter = 0.2, 
  nqx1 = 1, nqx2 = 1, nqx3 = 1, 
  x_gamma_extrapolation = .true.,
  exxdiv_treatment = 'gygi-baldereschi',
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 200,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF
  
K_POINTS (automatic)
8 8 8 0 0 0
  
CELL_PARAMETERS (angstrom)
{cell}

ATOMIC_POSITIONS (crystal)
C  -0.0000000000       -0.0000000000       -0.0000000000
C   0.2503890466        0.2503890466        0.2503890466
"""

def scale_cell(cell, factor):
    return [tuple(v * factor for v in row) for row in cell]

def format_cell(cell):
    return "\n".join(
        f"  {row[0]: .9f}   {row[1]: .9f}   {row[2]: .9f}" for row in cell
    )

os.makedirs(outdir, exist_ok=True)
print(f"{'factor':<8}file")
for i, s in enumerate(scale_factors):
    scaled = scale_cell(base_cell, s)
    folder = os.path.join(outdir, f"{s:.2f}")
    os.makedirs(folder, exist_ok=True)
    tag = f"{i:02d}_s{s:.2f}"
    qe_fname = os.path.join(folder, f"{name}.in")
    qe_content = TEMPLATE.format(tag=tag, cell=format_cell(scaled))
    with open(qe_fname, "w") as f:
        f.write(qe_content)
    print(f"{s:<8}{qe_fname}")
