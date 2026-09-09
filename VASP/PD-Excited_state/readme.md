# Steps for VASP calculations: Excited States

Steps for VASP calculations using PBE and HSE06 functionals.

Check the [VASP](https://vasp-at.translate.goog/wiki/The_VASP_Manual?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true) manual.

**Necessary input files:** INCAR, POSCAR, KPOINTS, jobfile, and POTCAR. Each input file is explained in the [VASP-Inputs](https://vasp.at/wiki/Input_and_Output_-_a_short_Intro) documentation.

⚠️**Warning:** VASP is proprietary software. If you want to perform calculations using VASP, you must obtain and use the software legally. Therefore, **POTCAR files are not included in this repository**.

## 1. Delta Self-Consistent Field (ΔSCF) method
Exited states can also be studied in Quantum ESPRESSO using the Delta Self-Consistent Field (ΔSCF) method. This method allows electrons to be promoted from an occupied energy level to an unoccupied one by specifying the occupations.

Within the Franck-Condon approximation, the electronic excitation is much faster than the nuclear motion. Thus, ΔSCF can be used for calculating excited state properties such as vertical absorption and vertical emission energy. Furthermore, this method can also be used to calculate the Zero Phonon Line (ZPL) by performing a full atomic relaxation in the excited state configuration and thus account for the Stockes shifts. This method is commonly used for calculating the optical properties of point defects in semiconductors and insulators.

## 2. Zero Phonon Line (ZPL) calculation
The ZPL is the optical transition between the electronic ground and excited states without creating or absorbing phonons, meaning the lattice remains in the same vibrational state. It corresponds to the purely electronic transition energy and is therefore directly related to the energy difference between the relaxed ground- and excited-state configurations. In experiments, the ZPL appears as a sharp spectral feature, while the surrounding phonon sidebands arise from electron–phonon coupling.

>Note:
The ZPL represents the purely electronic transition, i.e., a transition without phonon participation, between the lowest potential energy surfaces (PESs) of the ground and excited states.

This quantity is computed as follows:

$$
E_{ZPL} = E_{e}(Q_{e}) - E_{g}(Q_{g}),
$$

where $$E_{ZPL}$$ is the ZPL energy, $$E_{e}(Q_{e})$$ is the energy of the excited state at its equilibrium configuration $$Q_{e}$$, and $$E_{g}(Q_{g})$$ is the energy of the ground state at its equilibrium configuration $$Q_{g}$$.

For our example, NV center in diamond, $$E_{e}(Q_{e})$$ is obtained from our previous ground state calculation in the [NV-1 folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/PD-Supercells/Calculations/PBE/defect/NV-1). However, for the excited state calculation, the input file must be created. To create the excited state input, first, the electronic transition must be determined using the ground state Kohn–Sham level diagram.
