# Steps for Quantum ESPRESSO calculations: Phonons

Steps for Quantum ESPRESSO calculations using **PBE** functional. Native phonon calculations in Quantum ESPRESSO are not implemented for hybrid functionals: https://www.quantum-espresso.org/Doc/ph_user_guide/node7.html.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/Figures/phon_qe_workflow.png)

## 1. Relaxation
The aim of the relaxation calculation is to find the most stable arrangement of atoms by minimizing total energy, reducing internal forces to zero, and optimizing cell geometry. The calculation is performed in the same way as described in section **1.3. Relaxation** in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive).

## 2. Self-Consistent Field (SCF) calculation
The aim of this calculation is to get the converged charge density and wavefunctions of the unperturbed system. The calculation is performed in the same way as described in section **1.4. Self-Consistent Field (SCF) calculation** in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive).

## 3. Dynamic Matrix (DM) calculation
Quantum ESPRESSO uses Density-Functional Perturbation Theory (DFPT) via the **ph.x** code to compute the dynamical matrix and phonon properties without needing supercells. By evaluating the second derivatives of the total energy with respect to atomic displacements, DFPT efficiently yields the interatomic force constants and vibrational frequencies for specific **q**-vectors. Therefore, the aim of this calculation is to compute the first-order change in the potential and wavefunctions for a chosen wavevector **q**, generating the dynamical matrix elements.

> **NOTE:** Instead of physically moving an atom and repeating a complete ground-state calculation for every possible displacement, DFPT calculates the response mathematically for an infinitesimally small disturbance (linear-response calculation, **linear** because the displacement is considered infinitesimally small). When an atom moves, the electrons rearrange, and this changes the forces acting on all the atoms around it. The calculation determines these changes in force and therefore learns how strongly the atoms interact when they vibrate. It does this for different wavelengths and directions of vibration throughout the crystal's reciprocal space. The main result is information describing the vibrational behavior of the crystal at those sampled points.

This type of calculation can be performed by setting up the input file as follows:
```bash
&INPUTPH
  outdir = '../tmp/'
  prefix = 'diamond'
  tr2_ph = 1d-14
  ldisp = .true.
  epsil = .true.
!  recover = .true.
  nq1 = 6
  nq2 = 6
  nq3 = 6
  fildyn = 'diamond.dyn'
/
```
The meaning of each tag is described in the [hp.x Input Description](https://www.quantum-espresso.org/Doc/INPUT_HP.html). The input file can be executed using the following command:
```bash
ph.x -inp dyn-matrix_ph.in > dyn-matrix_ph.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 ph.x -inp dyn-matrix_ph.in > dyn-matrix_ph.out
```
where **20** represents the number of CPU cores used for the calculation. An example of these calculations can be found in the [folder]().

## 4. Inverse Fourier Transform of the DM calculation 
Transform the dynamical matrices from a uniform **q**-mesh into real-space Interatomic Force Constants (IFCs). The **ph.x** calculation gives information in reciprocal space, but we want to know something more intuitive: how does one atom affect another atom when it moves?. **q2r.x** performs a Fourier transformation of the dynamical matrices and produces the real-space IFCs.

> **NOTE:** This calculation takes the vibrational information obtained at different points in reciprocal space (from the previous calculation) and converts it into a real-space description of the interactions between atoms. Conceptually, it changes the question from "how does the crystal respond to a vibration with this particular wavelength?" to "how does the force on one atom change when another atom moves?" The result is a collection of force constants describing the strength of interactions between atoms at different positions in the crystal. This step is essentially a change of representation: the physical information from the phonon calculation is reorganized into a form that describes the crystal's local atomic interactions.

## 5. Fourier Transformation of the real space calculation 
Perform an inverse Fourier transform back to any arbitrary **q**-point to plot phonon dispersions or calculate density of states (DOS). Now we have the real-space force constants, so **matdyn.x** can calculate phonons at whatever q-points we want. At each point along the high-symmetry path, **matdyn.x** constructs the dynamical matrix and solves an eigenvalue problem.

> **NOTE:** This calculation uses those real-space atomic interactions to determine the vibrational modes at any wavevector you are interested in. This is important because the previous calculation only explicitly sampled a finite grid of points. Once the real-space force constants are known, the program can reconstruct the vibrational behavior at new points without performing another expensive DFPT calculation at every one of them. You therefore specify a path through reciprocal space, usually passing through important high-symmetry points, and the program calculates the possible vibrational frequencies along that path.

## 6. Phonon Dispersion Relation (Band Structure) calculation
The resulting phonon dispersion tells you how the allowed vibrational frequencies change with the wavelength and direction of the vibration.

## 7. Density Of States (DOS) calculation

## 8. Projected Density Of States (PDOS) calculation

