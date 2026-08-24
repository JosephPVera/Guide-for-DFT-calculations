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

An example can be found in the [NV-1_excited](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Excited_state-PD/ZPL/PBE/NV-1_excited) folder, where the occupations are set up as follows:

$$
\begin{aligned}
&1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad \color{red}{0.0} \\
& {\color{green}{0.5\quad 0.5}} \quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0
\end{aligned}
$$

In the ground-state Kohn–Sham level diagram, the occupations are set up as follows:

$$
\begin{aligned}
&1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad 1.0\quad \color{blue}{1.0} \\
& {\color{red}{0.0\quad 0.0}} \quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0\quad 0.0
\end{aligned}
$$

>Note: For cases where electrons are promoted to doubly degenerate unoccupied levels, the calculations can become unstable and difficult to converge. To overcome this problem, the occupation is split equally (50–50) between the two energy levels. This problem comes from the Jahn-Teller theorem: any non-linear system occupying a degenerate electronic state is inherently unstable and will spontaneously distort to lift that degeneracy, lowering both the symmetry and the total energy. In a self-consistent DFT calculation, if you try to place a full electron in one of the two degenerate orbitals, the SCF cycle has no symmetry-protected reason to prefer one orbital over the other - small numerical noise breaks the degeneracy, the density mixes chaotically between the two nearly-degenerate solutions each iteration (charge sloshing), and convergence oscillates or fails outright.By imposing a 50–50 fractional occupation across the two degenerate levels, you constrain the electron density to retain the full symmetry of the underlying orbital manifold (rather than letting the solver arbitrarily collapse into one symmetry-broken component). This stabilizes the SCF cycle and gives a well-defined, reproducible total energy for the symmetric configuration.

**Reminder:** The excited state calculations must start with a **magnetization calculation** if the total magnetization is unknown. Then, the calculation proceeds with the **relaxation**, **SCF**, **NSCF**, and **PDOS** calculations. Check the steps in the [Supercell-PD](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD) folder, specifically Section 1.3.2.

Finally, the ZPL energy is:

$$
E_{ZPL} = -3971.22599987 - (-3971.35123692) = 0.12523705\ \mathrm{Ry}
$$

$$
E_{ZPL} = 1.7039382292\ \mathrm{eV}
$$

## 3. Configuration Coordinate
<p align="center">
  <img src="https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Excited_state-PD/Figures/ccd.png" alt="Descripción de la imagen">
</p>
