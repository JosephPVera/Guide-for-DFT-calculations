--- 
# Steps for VASP calculations: Relax, DOS, PDOS, Band Structure, and Charge Density
---

Steps for VASP calculations using PBE and HSE06 functionals.

Check the [VASP](https://vasp-at.translate.goog/wiki/The_VASP_Manual?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true) manual.

**Necessary input files:** INCAR, POSCAR, KPOINTS, jobfile, and POTCAR. Each input file is explained in the [VASP-Inputs](https://vasp.at/wiki/Input_and_Output_-_a_short_Intro) documentation.

⚠️**Warning:** VASP is proprietary software. If you want to perform calculations using VASP, you must obtain and use the software legally. Therefore, **POTCAR files are not included in this repository**.

---
# 1. PBE functional
---

## 1.1. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Primitive/Figures/vasp_workflow_pbe.png)

## 1.2. Convergence tests
The first step in obtaining accurate results is to perform convergence tests for parameters such as the **energy cutoff for wavefunctions**, and **k-point mesh**. These parameters can be modified through **ENCUT** in the **INCAR** file and the **k-point mesh** in the **KPOINTS** file.  

### 1.2.1. Energy cutoff for wavefunctions
Create several folders named according to the energy cutoff values to be used. For example:
```bash
mkdir {200..950..50}
```
Then, create the **POSCAR** file for the system under study. Several systems can be found in [The Material Project](https://next-gen.materialsproject.org/). An example of what a **POSCAR** file looks like is shown below:
```bash
C8
1.0
        2.5173001289         0.0000000000         0.0000000000
        1.2586500645         2.1800458606         0.0000000000
        1.2586500645         0.7266819535         2.0553669484
    C
    2
Direct
     0.250000000         0.250000000         0.250000000
     0.000000000         0.000000000         0.000000000
```
Create the **INCAR** file. For convergence tests, the calculations do not need to be highly accurate, so the **INCAR** file can be configured as follows:
```bash
ALGO   = Fast      
NELMIN = 4         
EDIFF  = 1E-6      
ENCUT  = 200
PREC   = Normal    
LREAL  = .FALSE.      
ISMEAR = 0        
SIGMA  = 0.2       
ISPIN  = 1         

NSW    = 0         

LWAVE  = .FALSE.  

NPAR    = 4
NCORE = 7
```
Create the **KPOINTS** file. An example of what a **KPOINTS** file looks like is shown below:
```bash
k-density: 4.0
0
Gamma
 10 10 10
 0  0  0
```
Create the **jobfile** file. An example of what a **jobfile** file looks like is shown below:
```bash
#!/bin/bash
# Specify jobname:
#SBATCH --job-name=Joseph
# Specify the number of nodes and the number of CPU's (tasks) per node:
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH -p alto
# The maximum time allowed for the job, in hh:mm:ss
#SBATCH --time=24:00:00
# Maximum memory allowed per cpu
#SBATCH --mem-per-cpu=4G

ulimit -s unlimited
ulimit -a

PROG=vasp

## Run command 
mpirun -np $SLURM_NTASKS vasp_std

exit 0
```
Finally, use the **POTCAR** files provided for **VASP**. If your system consists of only one species, such as diamond, you only need to use the **POTCAR** file for carbon. On the other hand, if your system consists of two or more species, such as cubic boron nitride or BC2N, you must concatenate the **POTCAR** files for each species, following the order of the elements in the **POSCAR** file:
```bash
cat POTCAR_B POTCAR_N > POTCAR
```
```bash
cat POTCAR_B POTCAR_C POTCAR_N > POTCAR
```
Now that the input files are ready, copy them into all the folders:
```bash
for d in */; do cp INCAR POSCAR KPOINTS jobfile POTCAR "$d"; done
```
and change the **ENCUT** value in each folder accordingly:
```bash
for d in */; do sed -i "s/^ENCUT[[:space:]]*=.*/ENCUT  = ${d%\/}/" "$d/INCAR"; done
```
Run all the calculations at once using:
```bash
for dir in */;do cd $dir; sub jobfile; cd ../;done
```
Once the calculations are finished, extract the total energies using the [tot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/tot.py) script. An example of these calculations can be found in the [encut](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive/Calculations/PBE/convergence/cutoff) folder. As a result of the convergence analysis, it is possible to plot a convergence curve, as shown below:

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Primitive/Calculations/PBE/convergence/cutoff/delta_e_encut.png)

### 1.2.2. K-point mesh
Now, **ENCUT** value has been selected (for the diamond example, **ENCUT = 500**), the final step is to perform the convergence test for the **k-point mesh** using the **KPOINTS** file. Copy the input files corresponding to the converged **ENCUT** value, and then create several folders according to the **k-density** to be tested:
```bash
mkdir {1..9..1}
```
Now copy the input files into all the folders:
```bash
for d in */; do cp INCAR POSCAR jobfile POTCAR "$d"; done
```
Create the KPOINTS file for each folder using the [kmesh.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/kmesh.py) script:
```bash
for d in {1..9}; do (cd "$d" && kmesh.py --d "$d"); done
```
Run all the calculations at once using:
```bash
for dir in */;do cd $dir; sub jobfile; cd ../;done
```
Once the calculations are finished, extract the total energies using the [tot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/tot.py) script. An example of these calculations can be found in the [kdensity](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive/Calculations/PBE/convergence/kdensity) folder. As a result of the convergence analysis, it is possible to plot a convergence curve, as shown below:

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Primitive/Calculations/PBE/convergence/kdensity/delta_e_kpoint.png)

## 1.3. Relaxation
The aim of the relaxation calculation is to find the most stable arrangement of atoms by minimizing total energy, reducing internal forces to zero, and optimizing cell geometry. This type of calculation can be performed by setting up the **INCAR** file as follows:
```bash
ALGO   = Normal 
NELMIN = 4         
EDIFF  = 1E-6    
ENCUT  = 500      
PREC   = Normal    
LREAL  = .FALSE. 
ISMEAR = 0        
SIGMA  = 0.005       
ISPIN  = 1         

NSW    = 30         
IBRION = 2          
ISIF = 3           

LWAVE  = .FALSE.

NPAR    = 4
NCORE = 7 
```
Keep in mind that, for this and all subsequent calculations, the converged values of **ENCUT** and **k-point mesh** should be kept fixed. For the diamond calculation, use the converged values **ENCUT = 500** and **k-point mesh = 10 10 10** (**k-density = 4.0**) for all subsequent calculations.

Once the calculation is finished, the lattice parameters of the relaxed system can be found in the **CONTCAR** file. The converged forces can be extracted using the [forces.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/forces.py) script. For our example, the diamond calculation, this information can be found in the [relax](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive/Calculations/PBE/relax) folder. In addition, the crystal structure can be visualized using the [VESTA](https://jp-minerals.org/vesta/en/download.html) software.

## 1.4. Self-Consistent Field (SCF) calculation
The aim of the SCF calculation is to solve the Kohn-Sham equations iteratively to find the ground-state electron charge density, total energy, and converged electronic wavefunctions for a system at fixed atomic positions. At this point, the lattice parameters obtained from the **relaxation calculation** must be used. For this, the **CONTCAR** file must be renamed to **POSCAR**:
```bash
mv CONTCAR POSCAR
```
For this type of calculation, the **INCAR** file can be performed by setting up the input file as follows:
```bash
ALGO   = Normal        
EDIFF  = 1E-06          
NELM   = 100          
NELMIN = 4              
PREC   = Normal       
ENCUT  = 500            
LREAL  = .FALSE.         
ISMEAR = 0               
SIGMA  = 0.005

IBRION = -1            
NSW    = 0
ISPIN  = 1              

LWAVE  = .TRUE.         
LCHARG = .TRUE.   
LORBIT = 11           

NPAR    = 4
NCORE = 7 
```
An example of this calculation can be found in the [scf](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive/Calculations/PBE/properties/scf) folder. The total energy  can be extracted using the [tot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/tot.py) script. The electron charge density is stored in the **CHGCAR** file and can be visualized using [VESTA](https://jp-minerals.org/vesta/en/download.html), while the electronic wavefunctions are stored in the **WAVECAR** binary file.

## 1.5. Density Of States (DOS) calculation
The aim of the DOS calculation is to find the number of available electronic energy states per unit energy interval in a material. This type of calculation can be performed by setting up the **INCAR** file as follows:
```bash
ALGO   = Normal    
NELMIN = 4         
NELM   = 300       
EDIFF  = 1E-6      
ENCUT  = 500      
PREC   = Normal    
LREAL  = .FALSE.   
ISMEAR = -5        
SIGMA  = 0.005   
ISPIN  = 1         

NSW    = 0         
 
LWAVE  = .FALSE.  
NEDOS  = 3001     
!EMIN   = -25      
!EMAX   =  25      
LORBIT = 11 
ICHARG = 11       
 
NPAR    = 4
NCORE = 7
```
Before running the calculation, the **CHGCAR** file must be copied into this folder:
```bash
cp -r ../scf/CHGCAR . 
```
The DOS calculation is a Non-Self-Consistent Field (NSCF) calculation that uses the already converged electron charge density from the SCF calculation. Therefore, a denser **k-point mesh** must be used to ensure accurate electronic eigenvalues. The **Projected Density of States (PDOS)** can also be obtained from this same calculation. It reveals which atoms and angular momentum components (s, p, d, f, and so on) dominate bonding, hybridization, and the states near the Fermi level. Focuses on the chemical character of the states. It tells you how much a specific atom or orbital contributes to the energy levels.

An example of this calculation can be found in the [dos](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive/Calculations/PBE/properties/dos) folder. In addition, the total DOS and PDOS is stored in the **DOSCAR** file and can be plotted using the [dospo.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/Scripts/dospo.py) script.


