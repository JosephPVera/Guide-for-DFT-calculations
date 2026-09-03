--- 
# Steps for VASP calculations: Relax, DOS, PDOS, Band Structure, and Charge Density
---

Steps for VASP calculations using PBE and HSE06 functionals.

Check the [VASP](https://vasp-at.translate.goog/wiki/The_VASP_Manual?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true) manual.

**Necessary input files:** INCAR, POSCAR, KPOINTS, jobfile, and POTCAR. Each input file is explained in the (VASP-Inputs)[https://vasp.at/wiki/Input_and_Output_-_a_short_Intro]

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
Then, create the **POSCAR** file for the system under study. Several systems can be found in (The Material Project)[https://next-gen.materialsproject.org/]
