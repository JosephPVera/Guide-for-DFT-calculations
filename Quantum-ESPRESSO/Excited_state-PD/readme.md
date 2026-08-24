# Steps for Quantum ESPRESSO calculations: Excited States

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** functionals.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 1. Delta Self-Consistent Field (ΔSCF) method
Exited states can also be studied in Quantum ESPRESSO using the Delta Self-Consistent Field (ΔSCF) method. This method allows electrons to be promoted from an occupied energy level to an unoccupied one by specifying the occupations.

Within the Franck-Condon approximation, the electronic excitation is much faster than the nuclear motion. Thus, 
ΔSCF can be used for calculating excited state properties such as vertical absorption and vertical emission energy. Furthermore, this method can also be used to calculate the Zero Phonon Line (ZPL) by performing a full atomic relaxation in the excited state configuration and thus account for the Stockes shifts. This method is commonly used for calculating the optical properties of point defects in semiconductors and insulators.

## 2. Zero Phonon Line (ZPL) calculation
The ZPL is the optical transition between the electronic ground and excited states without creating or absorbing phonons, meaning the lattice remains in the same vibrational state. It corresponds to the purely electronic transition energy and is therefore directly related to the energy difference between the relaxed ground- and excited-state configurations. In experiments, the ZPL appears as a sharp spectral feature, while the surrounding phonon sidebands arise from electron–phonon coupling.

>Note:
The ZPL represents the purely electronic transition, i.e., a transition without phonon participation, between the lowest potential energy surfaces (PESs) of the ground and excited states.

This quantity is computed as follows:

$$
E_{ZPL} = E_{e}(Q_{e}) - E_{g}(Q_{g}),
$$

where $$E_{ZPL}$$ is the ZPL energy, $$E_{e}(Q_{e})$$ is the energy of the excited state at its equilibrium configuration $$Q_{e}$$, and $$E_{g}(Q_{g})$$ is the energy of the ground state at its equilibrium configuration $$Q_{g}$$.

For our example, NV center in diamond, $$E_{e}(Q_{e})$$ is obtained from our previous ground state calculation in the [NV-1 folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-1). However, for the excited state calculation, the input file must be created. To create the excited state input, first, the electronic transition must be determined using the ground state Kohn–Sham level diagram.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Excited_state-PD/Figures/transition-KSLD-ground_state.png) 

In this case, the most promising electronic transition occurs in the spin down channel, from the occupied energy level with band index 430 to the doubly degenerate unoccupied energy levels with band indices 431 and 432, given that these states are highly localized and isolated from the VBM and CBM. Now that the electronic transition has been determined, the input file for the excited-state calculation can be created using the ground-state input file, but with the **occupations = 'from_input'** tag added. This setting allows the electron to be promoted from energy level 430 to the degenerate levels 431–432 by specifying their occupations in the OCCUPATIONS section.
```bash
&SYSTEM
  ibrav =  0,
  nat  = 215,
  ntyp = 2,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  occupations = 'from_input',
  nspin       = 2
  tot_magnetization = 2.0
  nbnd = 862,
  tot_charge = -1.0
/
```
```bash
OCCUPATIONS
1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0
                 .
                 .
                 .
1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0
1.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
                 .
                 .
                 .
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0

1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0
                 .
                 .
                 .
1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 0.0
0.5 0.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
                 .
                 .
                 .
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0
```
**Reminder:** Keep in mind that the occupations must be specified for both the spin up and spin down channels and must be consistent with the number of bands (**nbnd**). 

An example can be found in the [NV-1_excited](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Excited_state-PD/ZPL/PBE/NV-1_excited) folder, where the 

$$
1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad
\color{blue}{0.0}
$$

$$
\color{red}{0.5\quad 0.5}\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0
$$

## 3. Configuration Coordinate
<p align="center">
  <img src="https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Excited_state-PD/Figures/ccd.png" alt="Descripción de la imagen">
</p>
