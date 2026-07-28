#!/usr/bin/env python3
# Written by Joseph P.Vera 
# 2025-09

# Convert Quantum ESPRESSO .in file to VASP POSCAR
# Usage: qe_convert.py input.in

import numpy as np
import sys
import re

BOHR_TO_ANG = 0.529177249  # Bohr radius in Angstroms 

def parse_qe_input(filename):
    with open(filename) as f:
        lines = f.readlines()

    data = {"celldm": {}}
    atomic_species, atomic_positions = [], []
    coord_type = "alat"

    i = 0
    while i < len(lines):
        line = lines[i].strip().lower()

        # SYSTEM block
        if line.startswith("ibrav"):
            data["ibrav"] = int(line.split("=")[1].replace(",", "").strip())
        if line.startswith("celldm"):
            match = re.findall(r"celldm\((\d+)\) *= *([0-9.eE+-]+)", line)
            for m in match:
                data["celldm"][int(m[0])] = float(m[1])

        # ATOMIC_SPECIES
        if line.startswith("atomic_species"):
            i += 1
            while i < len(lines) and lines[i].strip():
                parts = lines[i].split()
                if len(parts) < 3:
                    break
                atomic_species.append(parts[0])
                i += 1
            continue

        # ATOMIC_POSITIONS
        if line.startswith("atomic_positions"):
            if "alat" in line:
                coord_type = "alat"
            elif "angstrom" in line:
                coord_type = "angstrom"
            elif "crystal" in line:
                coord_type = "crystal"
            i += 1
            while i < len(lines) and lines[i].strip():
                parts = lines[i].split()
                if len(parts) < 4:
                    break
                atomic_positions.append((parts[0], list(map(float, parts[1:4]))))
                i += 1
            continue

        # CELL_PARAMETERS
        if line.startswith("cell_parameters"):
                unit = "alat"  
                if len(line.split()) > 1:
                        unit = re.sub(r"[^a-z]", "", line.split()[1].lower())
                        #unit = line.split()[1].replace("{","").replace("}","").lower()
                vecs = []
                for j in range(1, 4):
                        if i + j < len(lines):
                                vecs.append(list(map(float, lines[i + j].split())))
                        else:
                                raise ValueError("CELL_PARAMETERS block incomplete")
                data["cell_parameters"] = (unit, np.array(vecs))
                i += 3
                continue



        i += 1

    data["atomic_species"] = atomic_species
    data["atomic_positions"] = atomic_positions
    data["coord_type"] = coord_type
    return data


def lattice_from_ibrav(data):
    # Use CELL_PARAMETERS if available
    if "cell_parameters" in data:
        unit, vecs = data["cell_parameters"]
        if unit == "alat":
            return vecs * data["celldm"].get(1, 1.0) * BOHR_TO_ANG
        elif unit == "angstrom":
            return vecs
        elif unit == "bohr":
            return vecs * BOHR_TO_ANG

    ibrav = data.get("ibrav", 0)
    a_bohr = data["celldm"].get(1, 1.0)
    a = a_bohr * BOHR_TO_ANG
    c = data["celldm"].get(3, 1.0) * a_bohr * BOHR_TO_ANG if 3 in data["celldm"] else a

    if ibrav == 0:
        raise ValueError("ibrav=0 requires CELL_PARAMETERS in the input file.")
    elif ibrav == 1:  # cubic P
        return np.array([[a,0,0],[0,a,0],[0,0,a]])
    elif ibrav == 2:  # cubic F
        return np.array([[0,a/2,a/2],[a/2,0,a/2],[a/2,a/2,0]])
    elif ibrav == 3:  # cubic I
        return np.array([[-a/2,a/2,a/2],[a/2,-a/2,a/2],[a/2,a/2,-a/2]])
    elif ibrav == 4:  # hexagonal
        return np.array([[a,0,0],[-a/2,a*np.sqrt(3)/2,0],[0,0,c]])
    elif ibrav == 6:  # tetragonal P
        return np.array([[a,0,0],[0,a,0],[0,0,c]])
    elif ibrav == 8:  # orthorhombic P
        b = data["celldm"].get(2,1.0) * a_bohr * BOHR_TO_ANG
        return np.array([[a,0,0],[0,b,0],[0,0,c]])
    else:
        raise ValueError(f"Unsupported ibrav: {ibrav}")


def convert_positions(data, lattice):
    a_bohr = data["celldm"].get(1,1.0)
    a_ang = a_bohr * BOHR_TO_ANG
    coords = []
    for atom, pos in data["atomic_positions"]:
        pos = np.array(pos)
        if data["coord_type"] == "alat":
            cart = pos * a_ang
        elif data["coord_type"] == "angstrom":
            cart = pos
        elif data["coord_type"] == "crystal":
            coords.append((atom,pos))
            continue
        else:
            raise ValueError("Unknown coord_type")

        # Convert to fractional coordinates
        frac = np.dot(np.linalg.inv(lattice.T), cart)
        coords.append((atom, frac))
    return coords


def write_poscar(filename, lattice, coords):
    species = []
    for atom,_ in coords:
        if atom not in species:
            species.append(atom)
    counts = [sum(1 for at,_ in coords if at==s) for s in species]

    with open(filename,"w") as f:
        f.write("Converted from QE input\n")
        f.write("1.0\n")
        for vec in lattice:
            f.write(f" {vec[0]:15.10f} {vec[1]:15.10f} {vec[2]:15.10f}\n")
        f.write(" ".join(species)+"\n")
        f.write(" ".join(map(str,counts))+"\n")
        f.write("Direct\n")
        for atom,pos in coords:
            f.write(f" {pos[0]:15.10f} {pos[1]:15.10f} {pos[2]:15.10f}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: qe_convert.py input.in")
        sys.exit(1)

    data = parse_qe_input(sys.argv[1])
    lattice = lattice_from_ibrav(data)
    coords = convert_positions(data, lattice)
    write_poscar("POSCAR", lattice, coords)
    print("POSCAR written successfully!")
