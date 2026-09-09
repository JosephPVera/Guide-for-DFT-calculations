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

## 3. Configuration Coordinate
A Configuration Coordinate Diagram (CCD) is a way to describe how the total energy of a system changes when the atomic configuration is displaced along a particular collective structural coordinate. It is widely used to analyze optical transitions, lattice relaxation, phonons, and electron–phonon coupling, especially for point defects. CCDs are based on the Franck–Condon approximation, which assumes that electronic transitions occur on a timescale much faster than nuclear motion. Therefore, the atomic configuration is effectively frozen during an optical transition, resulting in vertical transitions between the ground and excited state PES, while the subsequent lattice relaxation occurs on the corresponding PES. The difference between the equilibrium configurations of the two electronic states determines the relaxation energies and contributes to the Stokes shift. The CCD is depicted in the figure below:

<p align="center">
  <img src="https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/PD-Excited_state/Figures/ccd.png" alt="Descripción de la imagen">
</p>

Here, the blue curve represents the ground state PES, while the orange curve represents the excited state PES. In addition, the following quantities are also defined:
#### 1. Configuration coordinate ΔQ
The mass-weighted generalized displacement between the two relaxed geometries (ground and excited configurations):
   
$$
\begin{equation}
\Delta Q^{2} = \sum_{a} m_{a} \left| R_{\{e,a\}} - R_{\{g,a\}} \right|^{2}.
\end{equation}
$$
   
#### 2. Relaxation energies
How much energy each state releases when its geometry relaxes from the other state's minimum to its own:

$$
\Delta _{g} = \Delta _{AS} = E_{g}(Q_{e}) - E_{g}(Q_{g}),
$$

$$
\Delta _{e} = \Delta _{S} = E_{e}(Q_{g}) - E_{e}(Q_{e}).
$$

Here, $$Δ_{AS}$$ is the energy the ground state surface drops by, moving from $$Q_{e}$$ down to its true minimum $$Q_{g}$$, known as the anti-Stokes shift. Meanwhile, $$Δ_{S}$$ is the analogous   drop on the excited surface moving from $$Q_{g}$$ to $$Q_{e}$$, known as the Stokes shift.

#### 3. Absorption and emission energies
These are vertical transitions (Franck–Condon: the nuclei don't move during the fast electronic transition), so each keeps $$Q$$ fixed and only changes electronic state:

$$
E_{abs} = E_{e}(Q_{g}) - E_{g}(Q_{g}),
$$

$$
E_{em} = E_{e}(Q_{e}) - E_{g}(Q_{e}).
$$

Absorption starts from the ground-state equilibrium ($$Q_{g}$$) and jumps vertically onto the excited surface. Emission starts from the excited-state equilibrium ($$Q_{e}$$) and jumps vertically onto the ground surface.

#### 4. Zero Phonon Line (ZPL)
The purely electronic transition energy, between the two minima directly (not vertical):

$$
E_{ZPL} = E_{e}(Q_{e}) - E_{g}(Q_{g}).
$$

#### 5. Effective phonon frequencies
Each surface is modeled as a 1D harmonic oscillator in $$Q$$, with the origin at its own minimum:

$$
E_{i}(Q) = E_{i}(Q_{i}) + \frac{1}{2}\omega_{i}^{2}(Q - Q_{i})^{2}.
$$

Solving for $$\omega_{i}$$ using the relaxation energy:

$$
\Delta _{i} = \frac{1}{2}\omega_{i}^{2}\Delta Q^{2},
$$

where $$i$$ can take either the ground ($$g$$) or excited ($$e$$) state value. Therefore, 

$$
\hbar \omega_{i} = \hbar \frac{\sqrt{2\Delta _{i}}}{\Delta Q}.
$$

The two curves generally have different curvature, hence different frequencies. Keep in mind that $$\omega_{i}$$ is the angular frequency of the effective mode, and $$\hbar \omega_{i}$$ is the energy quantum of that mode. This energy is the energy difference between two vibrational levels.

#### 6. Huang-Rhys factor
The Huang–Rhys factor (**S**) is a dimensionless parameter that measures the strength of electron–phonon (or electron–vibrational) coupling in a material. In simple terms, it tells you how strongly an electronic excitation changes the equilibrium position of the atoms, causing the excitation to couple to lattice/molecular vibrations.
   - S <<< 1: weak electron–phonon coupling
     * The electronic transition produces relatively little lattice distortion.
     * The optical spectrum tends to be dominated by ZPL.
     * Phonon sidebands are weak.
   - S ~ 1: intermediate coupling
     * Vibrational/phonon-assisted transitions become significant.
     * Both the ZPL and phonon sidebands can be important.
   - S >>> 1: strong electron–phonon coupling
     * The electronic excitation substantially distorts the lattice.
     * The ZPL becomes relatively weak compared with the phonon sideband.
     * Many vibrational replicas can appear in the optical spectrum.

>Note: A particularly useful interpretation is that **S** is approximately the average number of phonons involved in the optical transition. It is important because it quantifies how strongly an electronic transition is coupled to lattice vibrations (phonons).

Therefore, **S** can be computed using the following relation (single harmonic mode model):

$$
S_{i} \approx \langle n_{phonon}\rangle = \frac{\Delta _{i}}{\hbar \omega_{i}},
$$

where $$i$$ can take either the ground ($$g$$) or excited ($$e$$) state value.

#### 7. Debye–Waller factor
The Debye–Waller factor (**D**) tells you what fraction of an optical transition occurs without creating or absorbing phonons. This factor is computed using **S** via the following relation:

$$
D_{i} = e^{-S_{i}}
$$

 >Note: For a point defect intended as a single-photon emitter, a high Debye–Waller factor is generally desirable because it means a larger fraction of photons are emitted into the sharp ZPL, rather than the broad phonon sideband.

To compute all the quantities outlined above, several configurations must be generated between the ground state configuration ($$Q_{g}$$) and the excited state configuration ($$Q_{e}$$). This can be done by interpolating configurations between $$Q_{g}$$ and $$Q_{e}$$ (remember to use the relaxed configurations in both cases). Now, run an SCF calculation for each case, first using the ground state input and then using the excited state input. Finally, after the calculations are completed, extract the total energies.
