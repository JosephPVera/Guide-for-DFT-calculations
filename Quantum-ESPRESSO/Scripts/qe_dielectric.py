#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

import glob
import os
import re

HEADER_RE = re.compile(r"Dielectric constant in cartesian axis")

def find_out_files():
    # Find all .out files in the current directory and all subfolders
    all_out_files = glob.glob("**/*.out", recursive=True)
    # Exclude files like slurm-0001.out, slurm-5768.out, etc. (checked by filename only)
    out_files = [f for f in all_out_files if not re.match(r"^slurm-\d+\.out$", os.path.basename(f))]
    return out_files

def get_last_dielectric_block(filepath):
    """Return the last 'Dielectric constant in cartesian axis' block as a string,
    or None if the file has no such section."""
    with open(filepath, "r", errors="ignore") as f:
        lines = f.readlines()

    indices = [i for i, line in enumerate(lines) if HEADER_RE.search(line)]
    if not indices:
        return None

    start = indices[-1]
    block = [lines[start]]
    i = start + 1

    # Skip blank line(s) right after the header
    while i < len(lines) and lines[i].strip() == "":
        block.append(lines[i])
        i += 1

    # Collect the matrix rows until the next blank line (or EOF)
    while i < len(lines) and lines[i].strip() != "":
        block.append(lines[i])
        i += 1

    return "".join(block).rstrip("\n")

def main():
    out_files = find_out_files()

    if not out_files:
        print("No .out files found.")
        return

    for f in sorted(out_files):
        block = get_last_dielectric_block(f)
        print(f"File read: {f}")
        if block:
            print(block)
        else:
            print("(no 'Dielectric constant in cartesian axis' section found)")
        print()

if __name__ == "__main__":
    main()
