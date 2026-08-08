# Steps for Quantum ESPRESSO calculations: Point Defects

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** functionals.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Figures/supercell_PD_workflow.png)

---
# 1. PBE functional
---
## 1.1. Primitive Cell Calculations
The steps for computing the properties of the primitive cell can be found in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive).

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
\mu^{elemental}_{B} = \frac{E_{B}}{N_{B}} = \frac{-80.439555}{12} = -6.703296  eV/atom
$$

while the elemental nitrogen chemical potential is:

$$
\mu^{elemental}_{N} = \frac{E_{N}}{N_{N}} = \frac{-16.633160}{2} = -8.316580  eV/atom
$$

Formation enthalpy of c-BN

$$
\Delta H_{f}(AB) = \mu_{BN} - \mu^{elemental}_{B} - \mu^{elemental}_{N} = -17.451456 - (-6.703296) - (-8.316580) = -2.431580  eV
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
\mu^{\ast}_{B} + \mu^{\ast}_{N} = -2.431580  eV.
$$

Under B-rich limit:

$$
\mu^{\ast}_{B} = 0,
$$
$$
\mu^{\ast}_{N} = -2.431580  eV.
$$

Under N-rich limit:

$$
\mu^{\ast}_{N} = 0,
$$
$$
\begin{equation}
\mu^{\ast}_{B} = -2.431580  eV.
\end{equation}
$$

**Diamond:** For our example, since the host material is composed of only one atomic species (carbon), the elemental chemical potentials will be used. The total energy of diamond can be extracted from the [C folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive/Calculations/PBE/properties/scf), while the total energy of nitrogen is obtained using a nitrogen dimer (N2), whose total energy can be extracted from the [N folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/cpd/N/scf). Therefore:

$$
\mu^{elemental}_{C} = \frac{E_{C}}{N_{C}} = \frac{-16.633160}{2} = -8.316580 &  eV/atom
$$

$$
\mu^{elemental}_{N} = \frac{E_{N}}{N_{N}} = \frac{-16.633160}{2} = -8.316580  eV/atom
$$

## 1.3. Working with Supercells
### 1.3.1. Convergence tests
#### 1.3.1.1. From convergence tests with the primitive cell
The initial parameters for the subsequent calculations will be taken from the previous calculations, namely those performed using the primitive cell. Furthermore, the relaxed structure obtained with the PBE functional for the primitive cell will be used as the initial structure for constructing the supercells. For the diamond example, in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive), the converged values **ecutwfc = 45.0** and **ecutrho = 180.0** will be used.

#### 1.3.1.2. Supercell
In this section, the relaxed primitive cell will be used to construct perfect and defective supercells of different sizes. In fact, the supercells will be constructed by simply repeating the primitive cell periodically along its lattice vectors. First, perfect supercells of different sizes (e.g.,1x1x1, 2x2x2, 3x3x3, and so on) will be constructed, depending on the crystal structure of the material. Then, these perfect supercells will be used to introduce simple defects, such as a single vacancy. Finally, the formation energy will be calculated for each case using the following equation:

$$E^{q=0}_{form}[D] = E^{q=0}_{def}[D] - E_{perf} - \sum \mu^{elemental}_{A}$$

Taking into account that, for this simple calculation, the defects will be considered in the neutral charge state (q=0). Now, it is possible to plot the formation energy as a function of the number of atoms and determine the optimal supercell size.

For our example, diamond, we will use a supercell containing 216 atoms (i.e., a 3x3x3 supercell).

