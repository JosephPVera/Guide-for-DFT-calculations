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
Then, create the **.in** file for the system under study. Next, copy the **.in** file into each of the created folders, modifying the **ecutwfc** parameter to match the energy cutoff value indicated by the corresponding folder name.
