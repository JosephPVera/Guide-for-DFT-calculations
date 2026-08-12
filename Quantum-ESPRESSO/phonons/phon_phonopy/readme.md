# Steps for Quantum ESPRESSO calculations: Phonons

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** functionals and [Phonopy](https://phonopy-github-io.translate.goog/phonopy/qe.html?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc#).

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/Figures/phon_phonopy_workflow.png)

---
# 1. PBE functional
---

## 1.1. Relaxation
The aim of the relaxation calculation is to find the most stable arrangement of atoms by minimizing total energy, reducing internal forces to zero, and optimizing cell geometry. The calculation is performed in the same way as described in section **1.3. Relaxation** in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive).

## 1.2. Supercell
[Phonopy](https://phonopy-github-io.translate.goog/phonopy/qe.html?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc#) uses the finite-displacement and supercell approach to calculate phonon properties by first creating a larger supercell of the crystal and then slightly displacing atoms from their equilibrium positions. For each displacement, it calculates the resulting atomic forces using a first-principles method such as DFT. Phonopy uses these forces to determine the interatomic force constants, which describe how strongly atoms interact when displaced. It then constructs the dynamical matrix and diagonalizes it to obtain the phonon frequencies and eigenvectors throughout the Brillouin zone.

Once the primitive cell has been relaxed, it will be used to construct the supercell with displacements using the following command:
```bash
phonopy --qe -d --dim="3 3 3" -c diamond_scf.in
```
After running the command, several files will be created (such as **supercell-001.in**, **supercell-002.in**, and so on). Now we must create a folder for each supercell:
```bash
mkdir dis-001 dis-002
```
Each input must be copied in their corresponding folder. For example:
```bash
cp -r supercell-001.in dis-001
```
The **supercell-001.in** input file must be set up as follows:
```bash
&CONTROL
  calculation = 'scf',
  prefix      = 'diamond',
  outdir      = './tmp/',
  pseudo_dir  = '../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  restart_mode = 'from_scratch',
  disk_io = 'low',
/

&SYSTEM
  ibrav =  0,
  nat  = 54,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 180.0,
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 200,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

CELL_PARAMETERS {bohr}
  -10.1257353488152297    0.0000000000000000   10.1257353488152297
    0.0000000000000000   10.1257353488152297   10.1257353488152297
  -10.1257353488152297   10.1257353488152297    0.0000000000000000
  
ATOMIC_SPECIES
  C   12.01070   C.pbe-n-kjpaw_psl.1.0.0.UPF
  
ATOMIC_POSITIONS {crystal}
  C   0.0013966527009207  0.0000000000000000  0.0000000000000000
  C   0.3333333333333333  0.0000000000000000  0.0000000000000000
                                   .
                                   .
                                   .
  C   0.4167963488666666  0.7501296822000000  0.7501296822000000
  C   0.7501296822000000  0.7501296822000000  0.7501296822000000
  
K_POINTS (automatic)
8 8 8 0 0 0
```
🔔**Reminder:** The order of the **CELL_PARAMETERS**, **ATOMIC_SPECIES**, **ATOMIC_POSITIONS** and **K_POINTS** sections in the input file is important for Phonopy to work properly.

Once the calculations are done, the **FORCE_SETS** file can be created using the following command:
```bash
phonopy -f dis-001/supercell-001.out dis-002/supercell-002.out
```
Examples of these calculations for diamond can be found in the [dis-001](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/dis-001) and [dis-002](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/dis-002) folders.

## 1.3. Non-analytical term correction (NAC)
The NAC is a correction applied to the phonon dynamical matrix to account for the long-range electrostatic interaction between atoms in polar or ionic materials. In such materials, vibrations of the ions can create a macroscopic electric polarization, which produces a long-range electric field that is not properly captured by the short-range force constants obtained from a conventional supercell calculation. This effect is especially important near the $\Gamma$-point (**q** $\longrightarrow$ 0), where it can cause the longitudinal optical (LO) and transverse optical (TO) phonon modes to split, known as **LO–TO splitting**. Phonopy incorporates this effect using the **Born effective charge tensors** and the **high-frequency dielectric constant**, which are obtained from a Density-Functional Perturbation Theory (DFPT) calculation in Quantum ESPRESSO using **ph.x**. These quantities are then stored in a **BORN** file and used by Phonopy to add the non-analytical contribution to the dynamical matrix.

### 1.3.1. Without NAC

#### 1.3.1.1. Density Of States (DOS) calculation
A phonon DOS calculation counts the number of available vibrational modes at each frequency. This type of calculation can be performed by setting up a **mesh.conf** file as follows:
```bash
ATOM_NAME = C	 
DIM = 3 3 3
MP = 8 8 8
```
Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **dos folder**. Finally, use the following command to plot the DOS:
```bash
phonopy -p -s mesh.conf
```

An example for diamond can be found in [dos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/dos). The DOS can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/dos/tdos.png)

#### 1.3.1.2. Thermal Properties calculation
Thermal properties calculation refers to computing free energy, heat capacity, and entropy of a crystal as functions of temperature, using standard statistical thermodynamics formulas applied to the phonon spectrum. The idea is that once phonon frequencies are known across a sampling mesh in reciprocal space, each phonon mode is treated as a quantum harmonic oscillator, and the thermodynamic quantities are obtained by summing contributions from all these modes at each temperature. Since it relies on a mesh, this calculation must be run together with the mesh-sampling tags (MESH, MP, etc.), and its accuracy depends on how dense that mesh is, though it converges quickly and isn't computationally expensive.

Use the same **mesh.conf** file as in the previous calculation. Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **thermal folder**. Finally, use the following command to plot the thermal properties:
```bash
phonopy -p -s -t  mesh.conf > thermal.dat
```
An example for diamond can be found in [thermal folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/thermal). The thermal properties can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/thermal/thermal_properties.png)

#### 1.3.1.3. Projected Density Of States (PDOS) calculation
A phonon PDOS calculation breaks down the vibrations to show the specific contributions of individual atoms (projects the total vibrational modes onto individual atoms). This type of calculation can be performed by setting up a **pdos.conf** file as follows:
```bash
ATOM_NAME = C
DIM = 3 3 3
MP = 8 8 8
PDOS = AUTO
```
Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **pdos folder**. Finally, use the following command to plot the PDOS:
```bash
phonopy -p -s pdos.conf
```
An example for diamond can be found in [pdos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/pdos). The PDOS can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/pdos/pdos.png)

#### 1.3.1.4. Phonon Dispersion Relation (Band Structure) calculation
The resulting phonon dispersion tells you how the allowed vibrational frequencies change with the wavelength and direction of the vibration. This type of calculation can be performed by setting up a **band.conf** file as follows:
```bash
ATOM_NAME = c
DIM =  3 3 3
BAND= 0.0 0.0 0.0   0.5 0.0 0.5   0.5 0.25 0.75   0.375 0.375 0.75   0.0 0.0 0.0   0.5 0.5 0.5   0.625 0.250 0.625   0.5 0.25 0.75   0.5 0.5 0.5  0.375 0.375 0.75
BAND_LABELS = $\Gamma$ X W K $\Gamma$ L U W L K 
# BAND_CONNECTION = .TRUE.
```
Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **band folder**. Finally, use the following command to plot the band structure:
```bash
phonopy -p -s band.conf
phonopy-bandplot --gnuplot band.yaml > band.dat
```
An example for diamond can be found in [band folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/band). The band structure can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/band/band.png)

Since diamond contains two atoms in the primitive cell, and each atom has three degrees of freedom, there should be six branches in the phonon band structure. These can be plotted separately using the **--split** tag.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/band/band-1.png)

### 1.3.2. With NAC
If the material being studied is polar, the NAC must be applied. For this, the following steps must be performed:

#### 1.3.2.1. Self-Consistent Field (SCF) calculation
The aim of this calculation is to get the converged charge density and wavefunctions of the unperturbed system. The calculation is performed in the same way as described in section **1.4. Self-Consistent Field (SCF) calculation** in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive). 

An example for diamond is also included in the [scf folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/nac/scf).

#### 1.3.2.2. Dynamic Matrix (DM) calculation
Quantum ESPRESSO uses **Density-Functional Perturbation Theory (DFPT)** via the **ph.x** code to compute the dynamical matrix and phonon properties without needing supercells. By evaluating the second derivatives of the total energy with respect to atomic displacements, DFPT efficiently yields the interatomic force constants and vibrational frequencies for specific **q**-vectors. Therefore, the aim of this calculation is to compute the first-order change in the potential and wavefunctions for a chosen wavevector **q**, generating the dynamical matrix elements.

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
The meaning of each tag is described in the [HP Input Description](https://www.quantum-espresso.org/Doc/INPUT_HP.html). The input file can be executed using the following command:
```bash
ph.x -inp dyn-matrix_ph.in > dyn-matrix_ph.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 ph.x -inp dyn-matrix_ph.in > dyn-matrix_ph.out
```
where **20** represents the number of CPU cores used for the calculation. Once the calculation is done, several **.dyn** files will be created. In addition, the dielectric tensor can also be extracted from the **.out** file.

An example of this calculation for diamond can be found in the [ph folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/nac/ph). The dielectric tensor can be extract using the [qe_dielectric.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_dielectric.py) script. The extracted information looks as follows:
```bash
          Dielectric constant in cartesian axis 

          (       5.895284817      -0.007680836      -0.007680836 )
          (      -0.007680836       5.895284817       0.007680836 )
          (      -0.007680836       0.007680836       5.895284817 )
```
Once the calculation is done, the **BORN** file can be created using the following command:
```bash
phonopy-qe-born ../scf/diamond_scf.in dyn-matrix_ph.out | tee BORN
```
This file contains the **dielectric constant tensor** in the second line, followed by the **Born effective charge tensors** for each atom in the primitive cell. This information is essential for applying the **NAC**.
```bash
# epsilon and Z* of atoms 1
   5.89528482   -0.00768084   -0.00768084   -0.00768084    5.89528482    0.00768084   -0.00768084    0.00768084    5.89528482 
   0.00000000    0.00000000    0.00000000    0.00000000    0.00000000    0.00000000    0.00000000    0.00000000    0.00000000
```
#### 1.3.2.3. Density Of States (DOS) calculation
For this calculation, the **mesh.conf**, **FORCE_SETS**, **phonopy_disp.yaml**, and **BORN** files must be copied to the **dos file**. Finally, use the following command to plot the DOS:
```bash
phonopy -p -s --nac mesh.conf
```
An example for diamond can be found in [dos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-nac/dos). Since diamond is a non-polar material, no changes are observed in the plot.

#### 1.3.2.4. Thermal Properties calculation
For this calculation, the **mesh.conf**, **FORCE_SETS**, **phonopy_disp.yaml**, and **BORN** files must be copied to the **thermal file**. Finally, use the following command to plot the thermal properties:
```bash
phonopy -p -s -t --nac mesh.conf > thermal.dat
```
An example for diamond can be found in [thermal folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-nac/thermal). Since diamond is a non-polar material, no changes are observed in the plot.

#### 1.3.2.4. Projected Density Of States (PDOS) calculation
For this calculation, the **pdos.conf**, **FORCE_SETS**, **phonopy_disp.yaml**, and **BORN** files must be copied to the **pdos file**. Finally, use the following command to plot the PDOS:
```bash
phonopy -p -s --nac pdos.conf
```
An example for diamond can be found in [pdos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-nac/pdos). Since diamond is a non-polar material, no changes are observed in the plot.

#### 1.3.2.5. Phonon Dispersion Relation (Band Structure) calculation
For this calculation, the **band.conf**, **FORCE_SETS**, **phonopy_disp.yaml**, and **BORN** files must be copied to the **band file**. Finally, use the following command to plot the band structure:
```bash
phonopy -p -s --nac band.conf
phonopy-bandplot --gnuplot band.yaml > band.dat
```
An example for diamond can be found in [band folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-nac/band). Since diamond is a non-polar material, no changes are observed in the plot.

![Alt text]()




