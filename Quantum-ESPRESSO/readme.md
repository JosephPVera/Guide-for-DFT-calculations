--- 
# Steps for Quantum ESPRESSO calculations: Relax, DOS, PDOS and Band Structure

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** pseudopotentials.

---
# 1. PBE functional
---

## 1.1. Workflow
![Alt text](https://github.com/JosephPVera/Quantum_espresso_software/blob/main/Examples/workflow/qe-workflow.png)

## 1.2. Convergence tests
The first step in obtaining accurate results is to perform convergence tests for parameters such as the **energy cutoff for wavefunctions**, **energy cutoff for charge density**, and **k-point mesh**. These parameters can be modified through the **ecutwfc** and **ecutrho** tags, as well as the **K_POINTS** section.  

### 1.2.1. Energy cutoff for wavefunctions
Create several folders named according to the energy cutoff values to be used. For example:
```bash
mkdir {10..80..5}
```
Then, create the **.in** file for the system under study. Next, copy the **.in** file into each of the created folders, modifying the **ecutwfc** parameter to match the energy cutoff value indicated by the corresponding folder name. For example, a **diamond.in** file can be used for a diamond calculation, as shown below:
```bash
&CONTROL
  calculation = 'scf',
  prefix      = 'diamond',
  outdir      = './tmp/',
  pseudo_dir  = '../../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  disk_io = 'nowf',
/

&SYSTEM
  ibrav =  2,
  celldm(1) = 6.74,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 10.0,
  nbnd = 8,
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF
  
ATOMIC_POSITIONS (alat)
C 0.00 0.00 0.00
C 0.25 0.25 0.25

K_POINTS (automatic)
10 10 10 0 0 0
```
