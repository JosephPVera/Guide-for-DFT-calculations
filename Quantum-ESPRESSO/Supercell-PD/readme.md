# Steps for Quantum ESPRESSO calculations: Point Defects

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** functionals.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Figures/supercell_PD_workflow.png)

---
# 1. PBE functional
---

## 1.2. Convergence tests
### 1.2.1. From convergence tests with the primitive cell
The initial parameters for the subsequent calculations will be taken from the previous calculations, namely those performed using the primitive cell. Furthermore, the relaxed structure obtained with the PBE functional for the primitive cell will be used as the initial structure for constructing the supercells.For the diamond example, in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive), the converged values **ecutwfc = 45.0** and **ecutrho = 180.0** will be used.

### 1.2.2. Supercell
In this section, the relaxed primitive cell will be used to construct perfect and defective supercells of different sizes. In fact, the supercells will be constructed by simply repeating the primitive cell periodically along its lattice vectors. First, perfect supercells of different sizes (e.g.,1x1x1, 2x2x2, 3x3x3, and so on) will be constructed, depending on the crystal structure of the material. Then, these perfect supercells will be used to introduce simple defects, such as a single vacancy. Finally, the formation energy will be calculated for each case using the following equation:

$$E^{q=0}_{form}[D] = E^{q=0}_{def}[D] - E_{perf} - \sum \mu^{elemental}_{A}$$

Taking into account that, for this simple calculation, the defects will be considered in the neutral charge state (q=0). Now, it is possible to plot the formation energy as a function of the number of atoms and determine the optimal supercell size.

For our example, diamond, we will use a supercell containing 216 atoms (i.e., a 3x3x3 supercell).

## 1.3. Competing Phases
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
\Delta H_{f}(AB) = \mu_{AB} - \mu^{elemental}_{A} - \mu^{elemental}_{B}
$$

For our example, due that the host material (diamond) only is compoud by one atomic species 
