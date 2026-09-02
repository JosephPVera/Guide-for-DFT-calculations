#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

"""
Convert an elk.in input file to a VASP POSCAR file.

Reads the scale, avec, and atoms blocks from an elk.in file and
writes an equivalent POSCAR (lattice vectors in Angstrom, atomic
positions in direct/fractional coordinates, grouped by species).
"""

import sys

BOHR_TO_ANG = 0.529177210903

def strip_comment(line):
    idx = line.find('!')
    if idx != -1:
        line = line[:idx]
    return line.strip()

def is_keyword_line(line):
    """A keyword line is a single bare token that isn't a number or a
    quoted string (elk convention: keyword alone on its own line)."""
    tokens = line.split()
    if len(tokens) != 1:
        return False
    tok = tokens[0]
    if tok.startswith("'") or tok.startswith('"'):
        return False
    try:
        float(tok.replace('d', 'e').replace('D', 'E'))
        return False
    except ValueError:
        return True

def parse_elk_in(path):
    with open(path) as f:
        raw_lines = f.readlines()

    lines = []
    for line in raw_lines:
        line = strip_comment(line)
        if line:
            lines.append(line)

    blocks = {}
    current_key = None
    for line in lines:
        if is_keyword_line(line):
            current_key = line.split()[0].lower()
            blocks.setdefault(current_key, [])
        else:
            if current_key is None:
                continue
            blocks[current_key].append(line)
    return blocks

def parse_atoms_block(data_lines):
    """Parse the 'atoms' block of elk.in"""
    idx = 0
    nspecies = int(data_lines[idx].split()[0])
    idx += 1

    species_list = []  # [(label, [(x, y, z), ...]), ...]
    for _ in range(nspecies):
        speciesfile = data_lines[idx].split()[0].strip("'\"")
        idx += 1
        label = speciesfile.split('.')[0]

        natoms = int(data_lines[idx].split()[0])
        idx += 1

        coords = []
        for _ in range(natoms):
            parts = data_lines[idx].split()
            x, y, z = (float(parts[0]), float(parts[1]), float(parts[2]))
            coords.append((x, y, z))
            idx += 1

        species_list.append((label, coords))

    return species_list

def build_poscar(blocks, comment="Converted from elk.in"):
    for required in ('scale', 'avec', 'atoms'):
        if required not in blocks:
            raise ValueError("elk.in is missing the '%s' block" % required)

    # --- scale factor(s) ---
    scale_tokens = []
    for line in blocks['scale']:
        scale_tokens.extend(line.split())
    scale_values = [float(t) for t in scale_tokens]
    if len(scale_values) == 1:
        scales = [scale_values[0]] * 3
    elif len(scale_values) == 3:
        scales = scale_values
    else:
        raise ValueError("Unexpected number of scale values: %d" % len(scale_values))

    # --- lattice vectors ---
    avec_tokens = []
    for line in blocks['avec']:
        avec_tokens.extend(line.split())
    avec_values = [float(t) for t in avec_tokens]
    if len(avec_values) != 9:
        raise ValueError("Expected 9 values in avec block, got %d" % len(avec_values))
    avec = [avec_values[0:3], avec_values[3:6], avec_values[6:9]]

    lattice_bohr = [[vec[i] * scales[i] for i in range(3)] for vec in avec]
    lattice_ang = [[c * BOHR_TO_ANG for c in vec] for vec in lattice_bohr]

    # --- atoms ---
    species_list = parse_atoms_block(blocks['atoms'])

    # --- assemble POSCAR text ---
    out = [comment, "1.0"]
    for vec in lattice_ang:
        out.append("  {:.10f}  {:.10f}  {:.10f}".format(*vec))

    labels = [label for label, _ in species_list]
    counts = [len(coords) for _, coords in species_list]
    out.append("  " + "  ".join(labels))
    out.append("  " + "  ".join(str(c) for c in counts))
    out.append("Direct")

    for label, coords in species_list:
        for (x, y, z) in coords:
            out.append("  {:.10f}  {:.10f}  {:.10f}   {}".format(x, y, z, label))

    return "\n".join(out) + "\n"

def main():
    elk_path = sys.argv[1] if len(sys.argv) > 1 else "elk.in"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "POSCAR"

    blocks = parse_elk_in(elk_path)
    poscar_text = build_poscar(blocks)

    with open(out_path, "w") as f:
        f.write(poscar_text)

    print("Saved file: %s" % out_path)

if __name__ == "__main__":
    main()
