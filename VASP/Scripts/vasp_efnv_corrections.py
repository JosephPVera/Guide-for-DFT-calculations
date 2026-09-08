#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-09

"""
Usage:
      python3 vasp_efnv_corrections.py
      
eFNV is a model point charge.
   
VASP version: computes the eFNV energy correction (pc term + alignment term)

This merges what used to be two scripts:
    - efnv-pc_term.py        (STEP 1: point-charge term only, lattice-only)
    - efnv-alignment_term.py (STEP 2: alignment term from OUTCAR site
                               potentials, loads the pc term and sums both)
"""

import json
import numpy as np
from eFNV.efnv_corrections import (
    read_structure, read_site_potentials, compare_structures,
    HalfMaxFaceDistanceDefectRegion, FixedDistanceDefectRegion,
    compute_efnv_correction, AnisotropicEwald,
)

PERFECT_POSCAR = "../perfect/CONTCAR"
DEFECT_POSCAR = "CONTCAR"
PERFECT_OUTCAR = "../perfect/OUTCAR"
DEFECT_OUTCAR = "OUTCAR"

CHARGE = -3

# Static dielectric tensor (electronic + ionic contributions)
DIELECTRIC_TENSOR = np.eye(3) * 5.85679453

#DIELECTRIC_TENSOR = np.array([
#    [6.953135, 0.0,        0.0],
#    [0.0,        6.953154, 0.0],
#    [0.0,        0.0,        6.953101]
#])

# defect_region_radius: sites closer than this to the defect are excluded
# from the alignment-term average. AUTO_RADIUS=True refines it
# automatically by checking where the far-field potential is flat.
AUTO_RADIUS = True
RADIUS_ANGSTROM = False   # only used if AUTO_RADIUS = False

# Optional: override the automatically-detected defect position (None ->
# use compare_structures(...).defect_center_coord(), recommended).
DEFECT_FRAC_COORDS_OVERRIDE = None

OUTPUT_JSON = "correction.json"

# STEP 1: pc term (lattice + dielectric tensor + charge state)
defect_struct = read_structure(DEFECT_POSCAR)
lattice = defect_struct.lattice.matrix

ewald = AnisotropicEwald(lattice, DIELECTRIC_TENSOR)
pc_term = ewald.pc_energy(CHARGE)

#print(f"pc term : {pc_term:.16f} eV")

# STEP 2: alignment term (from pp.x electrostatic-potential cubes) 
perfect_struct = read_structure(PERFECT_POSCAR)
perfect_pot = read_site_potentials(PERFECT_OUTCAR)
defect_pot = read_site_potentials(DEFECT_OUTCAR)

# sanity check: structure and cube must be the same calculation
if len(perfect_struct) != len(perfect_pot):
    raise ValueError(
        f"PERFECT_POSCAR ({PERFECT_POSCAR}) has {len(perfect_struct)} atoms "
        f"but PERFECT_OUTCAR ({PERFECT_OUTCAR}) reports {len(perfect_pot)} "
        f"site potentials. These two files don't correspond to the same "
        f"calculation")
if len(defect_struct) != len(defect_pot):
    raise ValueError(
        f"DEFECT_POSCAR ({DEFECT_POSCAR}) has {len(defect_struct)} atoms "
        f"but DEFECT_OUTCAR ({DEFECT_OUTCAR}) reports {len(defect_pot)} "
        f"site potentials. These two files don't correspond to the same "
        f"calculation.")

# Auto-identify the defect 
comparison = compare_structures(perfect_struct, defect_struct)
print(f"\nDetected: {comparison.summary()}")

if DEFECT_FRAC_COORDS_OVERRIDE is not None:
    defect_frac_coords = np.array(DEFECT_FRAC_COORDS_OVERRIDE)
else:
    defect_frac_coords = comparison.defect_center_coord()
#print(f"defect_center_coord: {defect_frac_coords}")

# Match atoms common to both supercells 
mapping = comparison.atom_mapping()
defect_idx = np.array(sorted(mapping.keys()))
perfect_idx = np.array([mapping[d] for d in defect_idx])

site_frac_coords = comparison.defect_frac[defect_idx]
site_species = [comparison.defect_species[d] for d in defect_idx]
defect_site_potentials = defect_pot[defect_idx]
perfect_site_potentials = perfect_pot[perfect_idx]

# Defect_region_radius
correction = compute_efnv_correction(
    lattice=lattice, dielectric_tensor=DIELECTRIC_TENSOR, charge=CHARGE,
    defect_frac_coords=defect_frac_coords,
    site_frac_coords=site_frac_coords, site_species=site_species,
    defect_site_potentials=defect_site_potentials,
    perfect_site_potentials=perfect_site_potentials,
    defect_region_radius=HalfMaxFaceDistanceDefectRegion(sample_radius_ratio=1.0)
        .defect_region_radius(lattice),
)

if AUTO_RADIUS:
    radius = HalfMaxFaceDistanceDefectRegion(sample_radius_ratio=1.0) \
        .defect_region_radius(lattice)
    #print(f"defect_region_radius (pydefect default, max inscribed sphere): "
    #      f"{radius:.3f} A")
else:
    radius = FixedDistanceDefectRegion(RADIUS_ANGSTROM).defect_region_radius(lattice)
    #print(f"defect_region_radius (fixed): {radius:.3f} A")

# alignment term 
correction.defect_region_radius = radius
alignment_term = correction.alignment_correction

# Sanity check: compute_efnv_correction recomputes its own pc term
# internally. it should match the value computed in step 1 above to numerical precision.
if not np.isclose(correction.point_charge_correction, pc_term, rtol=1e-10):
    print(f"\nWARNING: pc term recomputed in step 2 "
          f"({correction.point_charge_correction:.16f}) differs from the "
          f"pc term computed in step 1 above ({pc_term:.16f}). Check that "
          f"CHARGE/DIELECTRIC_TENSOR/lattice are consistent.")

correction_energy = pc_term + alignment_term

print("\n--- eFNV correction ---")
print(f"pc term        : {pc_term:.16f} eV")
print(f"alignment term : {alignment_term:.16f} eV")
print(f"correction energy : {correction_energy:.16f} eV")

# save everything into a json file 
summary = {
    "@module": "efnv_correction_standalone",
    "@class": "DefectEnergySummary",
    "charge": CHARGE,
    "lattice": lattice.tolist(),
    "dielectric_tensor": np.asarray(DIELECTRIC_TENSOR).tolist(),
    "point_charge_correction": pc_term,
    "defect_region_radius": radius,
    "defect_frac_coords": list(defect_frac_coords),
    "energy_corrections": {
        "pc term": pc_term,
        "alignment term": alignment_term,
        "correction energy": correction_energy,
    },
    "sites": [
        {"specie": s.specie, "distance": s.distance,
         "potential": s.potential, "pc_potential": s.pc_potential}
        for s in correction.sites
    ],
}
with open(OUTPUT_JSON, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved file: {OUTPUT_JSON}")
