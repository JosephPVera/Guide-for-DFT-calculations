# Steps for VASP calculations: Excited States

Steps for VASP calculations using PBE and HSE06 functionals.

Check the [VASP](https://vasp-at.translate.goog/wiki/The_VASP_Manual?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true) manual.

**Necessary input files:** INCAR, POSCAR, KPOINTS, jobfile, and POTCAR. Each input file is explained in the [VASP-Inputs](https://vasp.at/wiki/Input_and_Output_-_a_short_Intro) documentation.

⚠️**Warning:** VASP is proprietary software. If you want to perform calculations using VASP, you must obtain and use the software legally. Therefore, **POTCAR files are not included in this repository**.

## 1. Delta Self-Consistent Field (ΔSCF) method
Exited states can also be studied in VASP using the [Delta Self-Consistent Field (ΔSCF)](https://vasp.at/wiki/Delta_self-consistent_field) method. This method allows electrons to be promoted from an occupied energy level to an unoccupied one by specifying the occupations.

Within the Franck-Condon approximation, the electronic excitation is much faster than the nuclear motion. Thus, ΔSCF can be used for calculating excited state properties such as vertical absorption and vertical emission energy. Furthermore, this method can also be used to calculate the Zero Phonon Line (ZPL) by performing a full atomic relaxation in the excited state configuration and thus account for the Stockes shifts. This method is commonly used for calculating the optical properties of point defects in semiconductors and insulators.

## 2. Zero Phonon Line (ZPL) calculation
The ZPL is the optical transition between the electronic ground and excited states without creating or absorbing phonons, meaning the lattice remains in the same vibrational state. It corresponds to the purely electronic transition energy and is therefore directly related to the energy difference between the relaxed ground- and excited-state configurations. In experiments, the ZPL appears as a sharp spectral feature, while the surrounding phonon sidebands arise from electron–phonon coupling.

>Note: The ZPL represents the purely electronic transition, i.e., a transition without phonon participation, between the lowest potential energy surfaces (PESs) of the ground and excited states.

This quantity is computed as follows:

$$
E_{ZPL} = E_{e}(Q_{e}) - E_{g}(Q_{g}),
$$

where $$E_{ZPL}$$ is the ZPL energy, $$E_{e}(Q_{e})$$ is the energy of the excited state at its equilibrium configuration $$Q_{e}$$, and $$E_{g}(Q_{g})$$ is the energy of the ground state at its equilibrium configuration $$Q_{g}$$.

For our example, NV center in diamond, $$E_{g}(Q_{g})$$ is obtained from our previous ground state calculation in the [N_C-V_C_-1](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/PD-Supercells/Calculations/PBE/defect/N_C-V_C_-1) folder. However, for the excited state calculation, the input file must be created. To create the excited state input, first, the electronic transition must be determined using the ground state Kohn–Sham level diagram.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/VASP/PD-Excited_state/Figures/transition-KSLD-ground_state.png) 

In this case, the most promising electronic transition occurs in the spin down channel, from the occupied energy level with band index 430 to the doubly degenerate unoccupied energy levels with band indices 431 and 432, given that these states are highly localized and isolated from the VBM and CBM. Now that the electronic transition has been determined, the **INCAR** file for the excited state calculation can be created using the ground state **INCAR** file, but with the **FERWE** and **FERDO** tags added.The **FERWE** tag controls the occupations in the spin up channel, while the **FERDO** tag controls the occupations in the spin down channel. This setting allows the electron to be promoted from energy level 430 to the degenerate levels 431–432 by specifying their occupations in the OCCUPATIONS section.
```bash
ALGO  =  Normal

PREC   =  Normal
LREAL  =  Auto
EDIFF  =  1e-06
ENCUT  =  500.0
NELM   =  100

ISIF    =  2
IBRION  =  2
EDIFFG  =  -0.01
NSW     =  200

ISMEAR  =  -2
SIGMA   =  0.005

# PROMOTING ELECTRON
FERWE = 432*1.0 216*0.0
FERDO = 429*1.0 1*0.0 1*1.0 217*0.0

ISPIN  =  2

LWAVE   =  False
LCHARG  =  False

LORBIT  =  10

NELECT  =  862.0

NPAR   =  4
NCORE  =  9
```
**Reminder:** Keep in mind that the occupations must be specified for both the spin up and spin down channels and must be consistent with the number of bands. See **PROCAR**, **OUTCAR** (NBANDS) or **EIGVAL** files generated during the ground state calculation.


An example can be found in the [N_C-V_C_-1-excited](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/VASP/PD-Excited_state/ZPL/PBE/N_C-V_C_-1-excited) folder, where the occupations are set up as follows:
```bash
FERWE = 432*1.0 216*0.0
FERDO = 429*1.0 1*0.0 1*1.0 217*0.0
```
In this case, the number of bands is **NBANDS = 648**.

>Note: For cases where electrons are promoted to doubly degenerate unoccupied levels, the calculations can become unstable and difficult to converge. To overcome this problem, the occupation is split equally (50–50) between the two energy levels. This problem comes from the Jahn-Teller theorem: any non-linear system occupying a degenerate electronic state is inherently unstable and will spontaneously distort to lift that degeneracy, lowering both the symmetry and the total energy. In a self-consistent DFT calculation, if you try to place a full electron in one of the two degenerate orbitals, the SCF cycle has no symmetry-protected reason to prefer one orbital over the other - small numerical noise breaks the degeneracy, the density mixes chaotically between the two nearly-degenerate solutions each iteration (charge sloshing), and convergence oscillates or fails outright.By imposing a 50–50 fractional occupation across the two degenerate levels, you constrain the electron density to retain the full symmetry of the underlying orbital manifold (rather than letting the solver arbitrarily collapse into one symmetry-broken component). This stabilizes the SCF cycle and gives a well-defined, reproducible total energy for the symmetric configuration.

Finally, the ZPL energy is:

$$
E_{ZPL} = -1933.269192 - (-1934.987194) = 1.718002\ \mathrm{eV}
$$
