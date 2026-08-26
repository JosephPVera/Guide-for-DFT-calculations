#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2025-06

"""
Generate a set of inputs along a linear configuration coordinate (CCD)
between a relaxed ground state structure and a relaxed excited state
structure, for both electronic configurations.

Default mode: VASP
    Reads POSCAR_ground and POSCAR_excited, linearly interpolates positions
    and cell between them, and writes one POSCAR per lambda value

Usage:
python3 ccd.py [--qe] [--n-images]

--qe: Quantum ESPRESSO.
    Reads two QE 'scf' input templates, ground_state.in and
    excited_state.in, that already contain everything needed to run a
    calculation 
"""

import argparse
import os
import re
import numpy as np

def get_lambdas(n_images):
    return np.linspace(0, 1, n_images)

def run_vasp(n_images):
    from ase.io import read, write

    ground_outdir = 'ground_state'
    excited_outdir = 'excited_state'

    R_g = read('POSCAR_ground', format='vasp')
    R_e = read('POSCAR_excited', format='vasp')

    assert len(R_g) == len(R_e), \
        "Ground and excited structures have different atom counts"
    assert list(R_g.get_chemical_symbols()) == list(R_e.get_chemical_symbols()), \
        "Atom ordering/species mismatch between ground and excited structures"

    os.makedirs(ground_outdir, exist_ok=True)
    os.makedirs(excited_outdir, exist_ok=True)

    for lam in get_lambdas(n_images):
        img = R_g.copy()
        img.positions = (1 - lam) * R_g.positions + lam * R_e.positions
        img.set_cell((1 - lam) * R_g.cell[:] + lam * R_e.cell[:],
                      scale_atoms=False)

        lam_str = f'{lam:.3f}'
        gdir = os.path.join(ground_outdir, lam_str)
        edir = os.path.join(excited_outdir, lam_str)
        os.makedirs(gdir, exist_ok=True)
        os.makedirs(edir, exist_ok=True)

        gpath = os.path.join(gdir, 'POSCAR')
        epath = os.path.join(edir, 'POSCAR')
        write(gpath, img, format='vasp', direct=True, sort=True)
        write(epath, img, format='vasp', direct=True, sort=True)

        print(f'lambda = {lam_str}  ->  {gpath}   {epath}')

    print(f'\nGenerated {n_images} POSCAR pairs in '
          f'"{ground_outdir}/" and "{excited_outdir}/"')

def get_nat(text):
    m = re.search(r'nat\s*=\s*(\d+)', text)
    if not m:
        raise ValueError("Could not find 'nat' in &SYSTEM")
    return int(m.group(1))

def parse_cell(text):
    """Return the 3x3 cell matrix (angstrom) and the exact header line
    used, e.g. 'CELL_PARAMETERS {angstrom}'."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().upper().startswith('CELL_PARAMETERS'):
            header = line.strip()
            vecs = []
            for j in range(i + 1, i + 4):
                vecs.append([float(x) for x in lines[j].split()])
            return np.array(vecs), header
    raise ValueError('CELL_PARAMETERS block not found')

def parse_positions(text, nat):
    lines = text.splitlines()
    idx = next(i for i, l in enumerate(lines)
               if l.strip().upper().startswith('ATOMIC_POSITIONS'))
    header = lines[idx].strip()
    species = []
    coords = []
    for j in range(idx + 1, idx + 1 + nat):
        parts = lines[j].split()
        species.append(parts[0])
        coords.append([float(x) for x in parts[1:4]])
    return species, np.array(coords), header, idx, idx + 1 + nat

def set_param(text, key, value):
    pattern = re.compile(
        r"(^\s*" + re.escape(key) + r"\s*=\s*).*?(,?\s*)$",
        re.MULTILINE
    )
    if isinstance(value, str):
        repl = r"\g<1>'" + value + r"'\g<2>"
    else:
        repl = r"\g<1>" + str(value) + r"\g<2>"
    new_text, n = pattern.subn(repl, text, count=1)
    if n == 0:
        raise ValueError(f"Parameter '{key}' not found to replace")
    return new_text

def build_image(template_text, nat, species, new_coords, new_cell):
    lines = template_text.splitlines()

    # --- swap ATOMIC_POSITIONS block ---
    _, _, pos_header, start, end = parse_positions(template_text, nat)
    new_pos_lines = [
        f"{sp:<3s}  {c[0]: .10f}  {c[1]: .10f}  {c[2]: .10f}"
        for sp, c in zip(species, new_coords)
    ]
    lines = lines[:start] + [pos_header] + new_pos_lines + lines[end:]
    text = '\n'.join(lines) + '\n'

    # --- swap CELL_PARAMETERS block ---
    _, cell_header = parse_cell(text)
    clines = text.splitlines()
    ci = next(i for i, l in enumerate(clines)
              if l.strip().upper().startswith('CELL_PARAMETERS'))
    new_cell_lines = [f"  {row[0]: .10f}  {row[1]: .10f}  {row[2]: .10f}"
                       for row in new_cell]
    clines = clines[:ci] + [cell_header] + new_cell_lines + clines[ci + 4:]
    text = '\n'.join(clines) + '\n'

    # --- keep prefix / outdir as given in the template ---
    m = re.search(r"prefix\s*=\s*'([^']+)'", text)
    base_prefix = m.group(1) if m else 'calc'
    text = set_param(text, 'prefix', base_prefix)

    m = re.search(r"outdir\s*=\s*'([^']+)'", text)
    base_outdir = m.group(1).rstrip('/') if m else '../tmp'
    text = set_param(text, 'outdir', base_outdir)

    return text

def run_qe(n_images):
    ground_outdir = 'ground_configs'
    excited_outdir = 'excited_configs'

    with open('ground_state.in') as f:
        ground_text = f.read()
    with open('excited_state.in') as f:
        excited_text = f.read()

    nat_g = get_nat(ground_text)
    nat_e = get_nat(excited_text)
    assert nat_g == nat_e, "Ground and excited templates have different nat"
    nat = nat_g

    sp_g, R_g, _, _, _ = parse_positions(ground_text, nat)
    sp_e, R_e, _, _, _ = parse_positions(excited_text, nat)
    assert sp_g == sp_e, "Atom ordering/species mismatch between templates"

    cell_g, _ = parse_cell(ground_text)
    cell_e, _ = parse_cell(excited_text)

    os.makedirs(ground_outdir, exist_ok=True)
    os.makedirs(excited_outdir, exist_ok=True)

    for lam in get_lambdas(n_images):
        coords_i = (1 - lam) * R_g + lam * R_e
        cell_i = (1 - lam) * cell_g + lam * cell_e

        ground_out = build_image(ground_text, nat, sp_g, coords_i, cell_i)
        excited_out = build_image(excited_text, nat, sp_e, coords_i, cell_i)

        lam_str = f'{lam:.3f}'
        gdir = os.path.join(ground_outdir, lam_str)
        edir = os.path.join(excited_outdir, lam_str)
        os.makedirs(gdir, exist_ok=True)
        os.makedirs(edir, exist_ok=True)

        gpath = os.path.join(gdir, 'scf.in')
        epath = os.path.join(edir, 'scf.in')
        with open(gpath, 'w') as f:
            f.write(ground_out)
        with open(epath, 'w') as f:
            f.write(excited_out)

        print(f'lambda = {lam:.4f}  ->  {gpath}   {epath}')

    print(f'\nDone: {n_images} ground inputs in "{ground_outdir}/", '
          f'{n_images} excited inputs in "{excited_outdir}/".')

def parse_args():
    p = argparse.ArgumentParser(
        description="Generate CCD-interpolated inputs between a ground and "
                     "excited state structure. Defaults to VASP; pass --qe "
                     "for Quantum ESPRESSO."
    )
    p.add_argument('--qe', action='store_true',
                    help="Quantum ESPRESSO mode (default: VASP). Reads "
                         "'ground_state.in' and 'excited_state.in'. VASP mode "
                         "reads 'POSCAR_ground' and 'POSCAR_excited'.")
    p.add_argument('--n-images', type=int, default=9,
                    help='Number of images along lambda = 0..1 (default: 9)')
    return p.parse_args()

def main():
    args = parse_args()
    if args.qe:
        run_qe(args.n_images)
    else:
        run_vasp(args.n_images)

if __name__ == '__main__':
    main()
