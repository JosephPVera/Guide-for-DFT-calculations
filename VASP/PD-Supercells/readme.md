--- 
# Steps for VASP calculations: Point Defects
---

Steps for VASP calculations using PBE and HSE06 functionals.

Check the [VASP](https://vasp-at.translate.goog/wiki/The_VASP_Manual?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true) manual.

**Necessary input files:** INCAR, POSCAR, KPOINTS, jobfile, and POTCAR. Each input file is explained in the [VASP-Inputs](https://vasp.at/wiki/Input_and_Output_-_a_short_Intro) documentation.

⚠️**Warning:** VASP is proprietary software. If you want to perform calculations using VASP, you must obtain and use the software legally. Therefore, **POTCAR files are not included in this repository**.

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/PD-Supercells/Figures/supercell_PD_workflow.png)

---
# 1. PBE functional
---

## 1.1. Primitive Cell Calculations
The steps for computing the properties of the primitive cell can be found in the [primitive](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive) folder.

## 1.2. Competing Phases
Competing phases are essential in point defect calculations because they determine the allowed chemical potentials of the constituent elements. These chemical potentials directly enter the formation energy equation, so ignoring competing phases can lead to physically unrealistic predictions. For a material composed of two atomic species, such as A and B, thermodynamic equilibrium requires:

$$
\mu_{AB} = \mu_{A} + \mu_{B},
$$

where:

$$
\mu_{A} = \mu^{elemental}_{A} + \mu^{\ast}_{A},
$$
$$
\mu_{B} = \mu^{elemental}_{B} + \mu^{\ast}_{B}.
$$

and where:

$$
\mu_{AB} = E_{AB}
$$
$$
\mu^{elemental}_{A} = \frac{E_{A}}{N_{A}},
$$
$$
\mu^{elemental}_{B} = \frac{E_{B}}{N_{B}},
$$

Therefore,

$$
\Delta H_{f}(AB) = \mu^{\ast}_{A} + \mu^{\ast}_{B}.
$$

Since AB is stable,

$$
\Delta H_{f}(AB) < 0
$$

Furthermore:

$$
\Delta H_{f}(AB) = \mu_{AB} - \mu^{elemental}_{A} - \mu^{elemental}_{B}.
$$

**Under A-rich condition**, when $$\mu_{A} = \mu^{elemental}_{A}$$. Then,

$$
\mu_{B} = \mu_{AB} - \mu^{elemental}_{A}.
$$

So, replacing:

$$
\mu^{\ast}_{A} = 0,
$$
$$
\mu^{\ast}_{B} = \mu_{AB} - \mu^{elemental}_{A} - \mu^{elemental}_{B}.
$$

**Under B-rich condition**, when $$\mu_{B} = \mu^{elemental}_{B}$$. Then,

$$
\mu_{A} = \mu_{AB} - \mu^{elemental}_{B}.
$$

So, replacing:

$$
\mu^{\ast}_{A} = \mu_{AB} - \mu^{elemental}_{A} - \mu^{elemental}_{B},
$$
$$
\mu^{\ast}_{B} = 0.
$$

**Example: For cubic Boron Nitrogen (c-BN)**

The total energy of c-BN is -17.451456 eV, whereas the total energies of rhombohedral $$\alpha$$-boron (containing 12 atoms) and the nitrogen dimer (N2) are -80.439555 eV and -16.633160 eV, respectively. 

The elemental boron chemical potential is:

$$
\mu^{elemental}_{B} = \frac{E_{B}}{N_{B}} = \frac{-80.439555}{12} = -6.703296\ \mathrm{eV/atom}
$$

while the elemental nitrogen chemical potential is:

$$
\mu^{elemental}_{N} = \frac{E_{N}}{N_{N}} = \frac{-16.633160}{2} = -8.316580\ \mathrm{eV/atom}
$$

Formation enthalpy of c-BN

$$
\Delta H_{f}(AB) = \mu_{BN} - \mu^{elemental}_{B} - \mu^{elemental}_{N} = -17.451456 - (-6.703296) - (-8.316580) = -2.431580\ \mathrm{eV/atom}
$$

Thermodynamic condition: The chemical potentials satisfy,

$$
\mu_{B} = \mu^{elemental}_{B} + \mu^{\ast}_{B},
$$
$$
\mu_{N} = \mu^{elemental}_{N} + \mu^{\ast}_{N}.
$$

gives

$$
\mu^{\ast}_{B} + \mu^{\ast}_{N} = -2.431580\ \mathrm{eV}.
$$

Under B-rich limit:

$$
\mu^{\ast}_{B} = 0,
$$
$$
\mu^{\ast}_{N} = -2.431580\ \mathrm{eV}.
$$

Under N-rich limit:

$$
\mu^{\ast}_{N} = 0,
$$
$$
\begin{equation}
\mu^{\ast}_{B} = -2.431580\ \mathrm{eV}.
\end{equation}
$$

**Diamond:** For our example, since the host material is composed of only one atomic species (carbon), the elemental chemical potentials will be used. The total energy of diamond can be extracted from the [C folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/Primitive/Calculations/PBE/properties/scf), while the total energy of nitrogen is obtained using a nitrogen dimer (N2), whose total energy can be extracted from the [N folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/PD-Supercells/Calculations/PBE/cpd/mol_N2). Therefore:

$$
\mu^{elemental}_{C} = \frac{E_{C}}{N_{C}} = \frac{-18.186080}{2} = -9.09304\ \mathrm{eV/atom}
$$

$$
\mu^{elemental}_{N} = \frac{E_{N}}{N_{N}} = \frac{-16.641762}{2} = -8.320881\ \mathrm{eV/atom}
$$
