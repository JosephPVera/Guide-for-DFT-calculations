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
Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **dos** folder. Finally, use the following command to plot the DOS:
```bash
phonopy -p -s mesh.conf
```

An example for diamond can be found in [dos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_phonopy/Calculations/PBE/plot-no-nac/dos).

#### 1.3.1.2. Thermal Properties calculation

#### 1.3.1.3. Projected Density Of States (PDOS) calculation

#### 1.3.1.4. Phonon Dispersion Relation (Band Structure) calculation

### 1.3.2. With NAC
