--- 
# Steps for Quantum ESPRESSO calculations: Phonons
--- 

Steps for VASP calculations using PBE and HSE06 functionals, and [Phonopy](https://phonopy-github-io.translate.goog/phonopy/qe.html?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc#).

Check the [VASP](https://vasp-at.translate.goog/wiki/The_VASP_Manual?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true) manual.

**Necessary input files:** INCAR, POSCAR, KPOINTS, jobfile, and POTCAR. Each input file is explained in the [VASP-Inputs](https://vasp.at/wiki/Input_and_Output_-_a_short_Intro) documentation.

⚠️**Warning:** VASP is proprietary software. If you want to perform calculations using VASP, you must obtain and use the software legally. Therefore, **POTCAR files are not included in this repository**.

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Phonons/Figures/phon_phonopy_workflow.png)

---
# 1. PBE functional
---

## 1.1. Relaxation
The aim of the relaxation calculation is to find the most stable arrangement of atoms by minimizing total energy, reducing internal forces to zero, and optimizing cell geometry. The calculation is performed in the same way as described in section **1.3. Relaxation** in the [primitive](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive) folder. An example is provided here in the [relax](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Phonons/phon_phonopy/Calculations/PBE/relax) folder.

## 1.2. Supercell
[Phonopy](https://phonopy-github-io.translate.goog/phonopy/qe.html?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc#) uses the finite-displacement and supercell approach to calculate phonon properties by first creating a larger supercell of the crystal and then slightly displacing atoms from their equilibrium positions. For each displacement, it calculates the resulting atomic forces using a first-principles method such as DFT. Phonopy uses these forces to determine the interatomic force constants, which describe how strongly atoms interact when displaced. It then constructs the dynamical matrix and diagonalizes it to obtain the phonon frequencies and eigenvectors throughout the Brillouin zone.

Once the primitive cell has been relaxed, it will be used to construct the supercell with displacements using the following command:
```bash
phonopy -d --dim="3 3 3"
```
After running the command, several files will be created (such as **POSCAR-001**, **POSCAR-002**, and so on). Now we must create a folder for each supercell:
```bash
mkdir dis-001 dis-002
```
Each input must be copied in their corresponding folder. For example:
```bash
cp -r POSCAR-001 dis-001
```
The **INCAR** file must be set up as follows:
```bash
ALGO   = Normal    
NELMIN = 4         
NELM = 100
EDIFF  = 1E-8     
ENCUT  = 500       
PREC   = Accurate  
LREAL  = .FALSE.  
ISMEAR = 1         
SIGMA  = 0.1   
ICHARG = 2

NSW    = 0         
IBRION = -1         
ISYM = 0

LWAVE = .FALSE.
LCHARG = .FALSE. 
 
NPAR    = 4
NCORE = 7 
```
Once the calculations are done, the **FORCE_SETS** file can be created using the following command:
```bash
phonopy -f dis-001/vasprun.xml dis-002/vasprun.xml
```
An example of this calculation for diamond can be found in the [dis-001](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/dis-001) folder.

## 1.3. Non-analytical term correction (NAC)
The NAC is a correction applied to the phonon dynamical matrix to account for the long-range electrostatic interaction between atoms in polar or ionic materials. In such materials, vibrations of the ions can create a macroscopic electric polarization, which produces a long-range electric field that is not properly captured by the short-range force constants obtained from a conventional supercell calculation. This effect is especially important near the $\Gamma$-point (**q** $\longrightarrow$ 0), where it can cause the longitudinal optical (LO) and transverse optical (TO) phonon modes to split, known as **LO–TO splitting**. Phonopy incorporates this effect using the **Born effective charge tensors** and the **high-frequency dielectric constant** (**electronic dielectric tensor**), which are obtained from a Density-Functional Perturbation Theory (DFPT) calculation in VASP. These quantities are then stored in a **BORN** file and used by Phonopy to add the non-analytical contribution to the dynamical matrix.

### 1.3.1. Without NAC

#### 1.3.1.1. Density Of States (DOS) calculation
A phonon DOS calculation counts the number of available vibrational modes at each frequency. This type of calculation can be performed by setting up a **mesh.conf** file as follows:
```bash
ATOM_NAME = C	 
DIM = 3 3 3
MP = 10 10 10
```
Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **dos folder**. Finally, use the following command to plot the DOS:
```bash
phonopy -p -s mesh.conf
```
An example for diamond can be found in [dos](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/dos) folder. The DOS can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/dos/tdos.png)

#### 1.3.1.2. Thermal Properties calculation
Thermal properties calculation refers to computing free energy, heat capacity, and entropy of a crystal as functions of temperature, using standard statistical thermodynamics formulas applied to the phonon spectrum. The idea is that once phonon frequencies are known across a sampling mesh in reciprocal space, each phonon mode is treated as a quantum harmonic oscillator, and the thermodynamic quantities are obtained by summing contributions from all these modes at each temperature. Since it relies on a mesh, this calculation must be run together with the mesh-sampling tags (MESH, MP, etc.), and its accuracy depends on how dense that mesh is, though it converges quickly and isn't computationally expensive.

Use the same **mesh.conf** file as in the previous calculation. Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **thermal folder**. Finally, use the following command to plot the thermal properties:
```bash
phonopy -p -s -t  mesh.conf > thermal.dat
```
An example for diamond can be found in [thermal](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/thermal) folder. The thermal properties can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/thermal/thermal_properties.png)


#### 1.3.1.3. Projected Density Of States (PDOS) calculation
A phonon PDOS calculation breaks down the vibrations to show the specific contributions of individual atoms (projects the total vibrational modes onto individual atoms). This type of calculation can be performed by setting up a **pdos.conf** file as follows:
```bash
ATOM_NAME = C
DIM = 3 3 3
MP = 10 10 10
PDOS = AUTO
```
Also, copy the **FORCE_SETS** and **phonopy_disp.yaml** to the **pdos folder**. Finally, use the following command to plot the PDOS:
```bash
phonopy -p -s pdos.conf
```
An example for diamond can be found in [pdos](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/pdos) folder. The PDOS can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/pdos/pdos.png)

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
An example for diamond can be found in [band](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/band) folder. The band structure can be plotted using the [phonplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/phonplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Phonons/phon_phonopy/Calculations/PBE/phon/plot-no-nac/band/band.png)

Since diamond contains two atoms in the primitive cell, and each atom has three degrees of freedom, there should be six branches in the phonon band structure. These can be plotted separately using the **--split** tag.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Phonons/phon_phonopy/Calculations/PBE/plot-no-nac/band/band-1.png)

