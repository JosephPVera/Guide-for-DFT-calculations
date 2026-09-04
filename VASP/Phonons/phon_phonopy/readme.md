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
