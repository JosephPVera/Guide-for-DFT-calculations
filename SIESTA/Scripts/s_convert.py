#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Convert a SIESTA .fdf input file to a VASP POSCAR file. The script automatically looks for a .fdf file in the current directory.

Supports:
  - LatticeConstant (Ang or Bohr)
  - LatticeVectors block
  - ChemicalSpeciesLabel block
  - AtomicCoordinatesAndAtomicSpecies block
  - AtomicCoordinatesFormat: Fractional / ScaledCartesian / NotScaledCartesianBohr / Ang
"""

import sys
import os
import glob

BOHR_TO_ANG = 0.52917721067

def find_fdf_file():
    """Look in the current directory for a .fdf file and return its path."""
    candidates = sorted(glob.glob("*.fdf"))
    if not candidates:
        print("Error: no .fdf file found in the current directory.")
        sys.exit(1)
    if len(candidates) > 1:
        print(f"Multiple .fdf files found: {candidates}")
        print(f"Using the first one: {candidates[0]}")
    return candidates[0]

def strip_comment(line):
    for marker in ("#", "!"):
        idx = line.find(marker)
        if idx != -1:
            line = line[:idx]
    return line.strip()

def read_fdf(path):
    with open(path, "r") as f:
        raw_lines = f.readlines()

    lines = [strip_comment(l) for l in raw_lines]
    lines = [l for l in lines if l]

    return lines

def get_scalar(lines, keyword):
    """Return the tokens following a scalar keyword (case-insensitive)."""
    for line in lines:
        parts = line.split()
        if parts and parts[0].lower() == keyword.lower():
            return parts[1:]
    return None

def get_block(lines, block_name):
    """Return the list of lines inside %block <block_name> ... %endblock."""
    start_tag = f"%block {block_name.lower()}"
    end_tag = f"%endblock {block_name.lower()}"
    inside = False
    content = []
    for line in lines:
        low = line.lower()
        if not inside and low.startswith("%block") and low.split(None, 1)[1] == block_name.lower():
            inside = True
            continue
        if inside and low.startswith("%endblock"):
            break
        if inside:
            content.append(line)
    return content

def parse_lattice_constant(lines):
    tokens = get_scalar(lines, "LatticeConstant")
    if tokens is None:
        raise ValueError("LatticeConstant not found in .fdf file")
    value = float(tokens[0])
    unit = tokens[1].lower() if len(tokens) > 1 else "ang"
    if unit.startswith("ang"):
        return value  # already in Angstrom
    elif unit.startswith("bohr"):
        return value * BOHR_TO_ANG
    else:
        raise ValueError(f"Unrecognized LatticeConstant unit: {unit}")

def parse_lattice_vectors(lines):
    block = get_block(lines, "LatticeVectors")
    if not block:
        raise ValueError("LatticeVectors block not found in .fdf file")
    vectors = []
    for line in block:
        vals = [float(x) for x in line.split()[:3]]
        vectors.append(vals)
    if len(vectors) != 3:
        raise ValueError("LatticeVectors block must contain exactly 3 vectors")
    return vectors

def parse_species(lines):
    block = get_block(lines, "ChemicalSpeciesLabel")
    if not block:
        raise ValueError("ChemicalSpeciesLabel block not found in .fdf file")
    species = {}
    for line in block:
        parts = line.split()
        idx = int(parts[0])
        symbol = parts[2]
        species[idx] = symbol
    return species

def parse_coordinates(lines, species):
    block = get_block(lines, "AtomicCoordinatesAndAtomicSpecies")
    if not block:
        raise ValueError("AtomicCoordinatesAndAtomicSpecies block not found")
    coords = []
    labels = []
    for line in block:
        parts = line.split()
        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
        spec_idx = int(parts[3])
        coords.append((x, y, z))
        labels.append(species[spec_idx])
    return coords, labels

def parse_coord_format(lines):
    tokens = get_scalar(lines, "AtomicCoordinatesFormat")
    if tokens is None:
        return "fractional"
    fmt = tokens[0].lower()
    return fmt

def write_poscar(out_path, system_name, lattice_const, vectors, species, coords, labels, coord_format):
    unique_labels = []
    for lab in labels:
        if lab not in unique_labels:
            unique_labels.append(lab)

    counts = [labels.count(lab) for lab in unique_labels]

    grouped_coords = []
    for lab in unique_labels:
        for c, l in zip(coords, labels):
            if l == lab:
                grouped_coords.append(c)

    with open(out_path, "w") as f:
        f.write(f"{system_name}\n")
        f.write("1.0\n") 
        for v in vectors:
            f.write(f"  {v[0]*lattice_const: .10f}  {v[1]*lattice_const: .10f}  {v[2]*lattice_const: .10f}\n")
        f.write("  " + "  ".join(unique_labels) + "\n")
        f.write("  " + "  ".join(str(c) for c in counts) + "\n")

        if coord_format.startswith("frac"):
            f.write("Direct\n")
        elif coord_format.startswith("scaledcart") or coord_format.startswith("ang"):
            f.write("Cartesian\n")
        elif coord_format.startswith("notscaledcartesianbohr"):
            f.write("Cartesian\n")
        else:
            f.write("Direct\n")

        for c in grouped_coords:
            if coord_format.startswith("notscaledcartesianbohr"):
                cx, cy, cz = (v * BOHR_TO_ANG for v in c)
            else:
                cx, cy, cz = c
            f.write(f"  {cx: .10f}  {cy: .10f}  {cz: .10f}\n")

def main():
    fdf_path = find_fdf_file()
    out_path = "POSCAR"

    lines = read_fdf(fdf_path)

    system_tokens = get_scalar(lines, "SystemName")
    system_name = " ".join(system_tokens) if system_tokens else "Converted from SIESTA fdf"

    lattice_const = parse_lattice_constant(lines)
    vectors = parse_lattice_vectors(lines)
    species = parse_species(lines)
    coord_format = parse_coord_format(lines)
    coords, labels = parse_coordinates(lines, species)

    write_poscar(out_path, system_name, lattice_const, vectors, species, coords, labels, coord_format)

    print(f"POSCAR written to: {out_path}")

if __name__ == "__main__":
    main()
