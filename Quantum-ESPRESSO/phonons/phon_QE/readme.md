# Steps for Quantum ESPRESSO calculations: Phonons

Steps for Quantum ESPRESSO calculations using **PBE** functional. Native phonon calculations in Quantum ESPRESSO are not implemented for hybrid functionals: https://www.quantum-espresso.org/Doc/ph_user_guide/node7.html.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/Figures/phon_qe_workflow.png)

## 1. Relaxation

## 2. Self-Consistent Field (SCF) calculation
Run a SCF calculation to get the converged charge density and wavefunctions of the unperturbed system.

## 3. Dynamic Matrix (DM) calculation
Quantum ESPRESSO uses Density-Functional Perturbation Theory (DFPT) via the **ph.x** code to compute the dynamical matrix and phonon properties without needing supercells. By evaluating the second derivatives of the total energy with respect to atomic displacements, DFPT efficiently yields the interatomic force constants and vibrational frequencies for specific q-vectors. Therefore, the aim of this calculation is to compute the first-order change in the potential and wavefunctions for a chosen wavevector **q**, generating the dynamical matrix elements.

## 4. Inverse Fourier Transform of the DM calculation 
Transform the dynamical matrices from a uniform **q**-mesh into real-space Interatomic Force Constants (IFCs).

## 5. Fourier Transformation of the real space calculation 
Perform an inverse Fourier transform back to any arbitrary **q**-point to plot phonon dispersions or calculate density of states (DOS).

## 6. Phonon Dispersion Relation (Band Structure) calculation

## 7. Density Of States (DOS) calculation

## 8. Projected Density Of States (PDOS) calculation
