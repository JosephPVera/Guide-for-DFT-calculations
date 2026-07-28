--- 
# Steps for Quantum ESPRESSO calculations: Relax, DOS, PDOS and Band Structure

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** pseudopotentials.

---
# 1. PBE functional
---

## 1.1. Workflow
![Alt text](https://github.com/JosephPVera/Quantum_espresso_software/blob/main/Examples/workflow/qe-workflow.png)

## 1.2. Convergence tests
The first step in obtaining accurate results is to perform convergence tests for parameters such us **energy cutoff for wavefunctions**, **energy cutoff for charge density**, and **k-point mesh**. These parameters can be modified through the **ecutwfc** and **ecutrho** tags, as well as the **K_POINTS** section.  


