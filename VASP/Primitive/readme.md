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

