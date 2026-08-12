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

**Diamond:** For our example, since the host material is composed of only one atomic species (carbon), the elemental chemical potentials will be used. The total energy of diamond can be extracted from the [C folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive/Calculations/PBE/properties/scf), while the total energy of nitrogen is obtained using a nitrogen dimer (N2), whose total energy can be extracted from the [N folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/cpd/N/scf). Therefore:

$$
\mu^{elemental}_{C} = \frac{E_{C}}{N_{C}} = \frac{-36.86713357}{2} = −18.433566785\ \mathrm{eV/atom}
$$

$$
\mu^{elemental}_{N} = \frac{E_{N}}{N_{N}} = \frac{-56.43341769}{2} = −28.216708845\ \mathrm{eV/atom}
$$

## 1.3. Working with Supercells

### 1.3.1. Convergence tests

#### 1.3.1.1. From convergence tests with the primitive cell
The initial parameters for the subsequent calculations will be taken from the previous calculations, namely those performed using the primitive cell. Furthermore, the relaxed structure obtained with the PBE functional for the primitive cell will be used as the initial structure for constructing the supercells. For the diamond example, in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive), the converged values we found were **ecutwfc = 45.0** and **ecutrho = 180.0**.

#### 1.3.1.2. Supercell
In this section, the relaxed primitive cell will be used to construct perfect and defective supercells of different sizes. In fact, the supercells will be constructed by simply repeating the primitive cell periodically along its lattice vectors. First, perfect supercells of different sizes (e.g.,1x1x1, 2x2x2, 3x3x3, and so on) will be constructed, depending on the crystal structure of the material. Then, these perfect supercells will be used to introduce the defects, such as vacancies, insterstitials or complexes. Finally, the formation energy will be calculated for each case using the following equation:

$$E^{q=0}_{form}[D] = E^{q=0}_{def}[D] - E_{perf} - \sum \mu^{elemental}_{A}$$

Taking into account that, for this simple calculation, the defects will be considered in the neutral charge state (q=0). Now, it is possible to plot the formation energy as a function of the number of atoms and determine the optimal supercell size.

**Diamond:** For our example, we will use a supercell containing 216 atoms (i.e., a 3x3x3 supercell).

### 1.3.2. Point Defects
Now the optimal supercell has been chosen, the defect to be studied can be introduced into the system. Once this is done, we will have two systems: the perfect supercell and the defective supercell. A folder will be created for the perfect supercell, such as [perfect folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/perfect). On the other hand, separate folders will be created for the defective supercell, each corresponding to a different charge state (e.g., -q, ..., -1, 0, +1, ..., +q).

**NV center in Diamond**: For our example, separate folders have been created for the different charge states, as shown in the [defect folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect).
```bash
mkdir NV{-3..2..1}
```

Once this is done, each system with its respective charge state must follow the steps below:

#### 1.3.2.1. Magnetization SCF
The aim of this calculation is to determine the total magnetization of the system through a self-consistent field (SCF) calculation. For this purpose, the input file must be set up as follows:
```bash
&CONTROL
  calculation = 'scf',
  prefix      = 'diamond_pd',
  outdir      = './tmp/',
  pseudo_dir  = '../../../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 5.0d-4,
  etot_conv_thr = 1.0d-4,
  restart_mode = 'from_scratch',
  nstep         = 140,
  disk_io = 'low',
/

&SYSTEM
  ibrav =  0,
  nat  = 215,
  ntyp = 2,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  occupations = 'smearing',
  smearing    = 'gaussian'
  degauss     = 0.005
  nspin       = 2
  starting_magnetization(1) = 0.0
  starting_magnetization(2) = 0.1
  nbnd = 864
  tot_charge = -3.0
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 100,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF
  N  14.0067 N.pbe-n-kjpaw_psl.1.0.0.UPF

K_POINTS (automatic)
1 1 1 0 0 0
  
CELL_PARAMETERS {angstrom}
  -7.5777929652         0.0000000000         7.5777929652
   4.3750408084         8.7500816165         4.3750408084
  -6.1872420470         6.1872420472        -6.1872420470

ATOMIC_POSITIONS (crystal)
C     0.000000000         0.000000000         0.000000000
C     0.000000000         0.000000000         0.333333333
                          .
                          .
                          .
C     0.750129682         0.916796349         0.916796349
N     0.416796349         0.416796349         0.416796000 
```
For this calculation, it is important to use the following tags:
```bash
  occupations = 'smearing',
  smearing    = 'gaussian'
  degauss     = 0.001
  nspin       = 2
  starting_magnetization(1) = 0.0
  starting_magnetization(2) = 0.1
```
This is because the **occupations = 'smearing'** tag allows the software to determine the total magnetization that minimizes the total energy of the system. Furthermore, a useful rule of thumb for determining the number of bands (**nbnd**) is to calculate the number of valence electrons, divide it by 2, and multiply the result by 1.5. 

$$
nbnd = \frac{N_{C}\times \text{(valence electrons of carbon)} + N_{N}\times \text{(valence electrons of nitrogen)}}{2}\times 1.5.
$$

Since supercells contain a large number of atoms, these calculations can be computationally demanding. Therefore, it is recommended to perform the calculation using only the Gamma point.

**NV center in diamond:** For our example, the number of bands should be:

$$
nbnd = \frac{214\times 4 + 1\times 5}{2}\times 1.5 = 645.75 \approx 646.
$$

However, for the purposes of this example and testing, we decided to use a larger number of bands.

Finally, the total magnetization of the system can be obtained using the following command:
```bash
grep "total magnetization" diamond_pd.out
```
This shows a list of data for each step, such as:
```bash
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =     0.01 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =     0.00 Bohr mag/cell
     total magnetization       =     0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
     total magnetization       =    -0.00 Bohr mag/cell
```
The last value corresponds to the correct total magnetization and will be used in the subsequent calculations. An example for NV-3 can be found in the [mag_scf folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/relax/mag_scf).

The **spin state** (**S**) can be determined from the total **magnetization** (**M**) using the following relation:

$$
M = 2S
$$

#### 1.3.2.2. Relaxation
In this calculation, the system will be relaxed using the total magnetization obtained previously. This relaxation optimizes only the atomic positions within the supercell. For this purpose, the input file must be set up as follows:
```bash
&CONTROL
  calculation = 'relax',
  prefix      = 'diamond_pd',
  outdir      = './tmp/',
  pseudo_dir  = '../../../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 5.0d-4,
  etot_conv_thr = 1.0d-4,
  restart_mode = 'from_scratch',
  nstep         = 140,
  disk_io = 'low',
/

&SYSTEM
  ibrav =  0,
  nat  = 215,
  ntyp = 2,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  occupations = 'fixed',
  nspin       = 2
  tot_magnetization = 0.0
  nbnd = 864
  tot_charge = -3.0
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 100,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

&IONS
  ion_dynamics = 'bfgs'  
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF
  N  14.0067 N.pbe-n-kjpaw_psl.1.0.0.UPF

K_POINTS (automatic)
1 1 1 0 0 0
  
CELL_PARAMETERS {angstrom}
  -7.5777929652         0.0000000000         7.5777929652
   4.3750408084         8.7500816165         4.3750408084
  -6.1872420470         6.1872420472        -6.1872420470

ATOMIC_POSITIONS (crystal)
C     0.000000000         0.000000000         0.000000000
C     0.000000000         0.000000000         0.333333333
                          .
                          .
                          .
C     0.750129682         0.916796349         0.916796349
N     0.416796349         0.416796349         0.416796000  
```
Since the total magnetization is fixed using the **tot_magnetization** tag, **occupations = 'fixed'** must be used. Once the calculation is done, the relaxed structure can be extracted using the [qe_lattice.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_lattice.py) script. The data will be displayed as follows:
```bash
ATOMIC_POSITIONS (crystal)
C                0.0001701107        0.0000647539        0.0000647542
C                0.0002602508        0.0003236124        0.3334611078
                          .
                          .
                          .
C                0.7500026446        0.9166624631        0.9166624627
N                0.4247437727        0.4087117851        0.4087117899
End final coordinates
```
An example for NV-3 can be found in the [relax folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/relax/relax).

⚠️ **WARNING**: If the system has convergence problems and does not reach self-consistency, continue using **occupations = 'smearing'** for the calculations. It is recommended to use a small **degauss** value. An example for NV-2 can be found in the [relax folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-2/relax/relax).

#### 1.3.2.3. Self-Consistent Field (SCF) calculation
For this calculation, the relaxed supercell must be used. Copy the **ATOMIC_POSITIONS** from the previous calculation and paste them into the input file. The input file must be set up as follows:
```bash
&CONTROL
  calculation = 'scf',
  prefix      = 'diamond_pd',
  outdir      = '../tmp/',
  pseudo_dir  = '../../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 5.0d-4,
  etot_conv_thr = 1.0d-4,
  restart_mode = 'from_scratch',
  nstep         = 140,
  disk_io = 'low',
/

&SYSTEM
  ibrav =  0,
  nat  = 215,
  ntyp = 2,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  occupations = 'fixed',
  nspin       = 2
  tot_magnetization = 0.0
  nbnd = 864,
  tot_charge = -3.0
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 100,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF
  N  14.0067 N.pbe-n-kjpaw_psl.1.0.0.UPF

K_POINTS (automatic)
1 1 1 0 0 0

CELL_PARAMETERS {angstrom}
  -7.5777929652         0.0000000000         7.5777929652
   4.3750408084         8.7500816165         4.3750408084
  -6.1872420470         6.1872420472        -6.1872420470

ATOMIC_POSITIONS (crystal)
C                0.0001701107        0.0000647539        0.0000647542
C                0.0002602508        0.0003236124        0.3334611078
                          .
                          .
                          .
C                0.7500026446        0.9166624631        0.9166624627
N                0.4247437727        0.4087117851        0.4087117899
```
Once the calculation is done, the total energy can be extract using the [qe_tot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_tot.py) script. An example for NV-3 can be found in the [scf folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/scf).

#### 1.3.2.4. Non-Self-Consistent Field (NSCF) calculation
If the calculations are performed using only the Gamma point, the NSCF calculation is not necessary. However, this step is included here for testing purposes. The input file is similar to the one used for the SCF calculation, with only the **calculation** tag changed as follows:
```bash
calculation = 'nscf'
```
Once the calculation is done, the Kohn-Sham level diagram can be plotted using the [qe_eig.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_eig.py) script. In this script, the VBM and CBM values must always be entered manually.

🔔**Reminder:** As mentioned previously, this calculation is not necessary when using only the Gamma point. Therefore, the Kohn–Sham level diagram should already be obtained from the SCF calculation.

An example for NV-3 can be found in the [nscf folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/nscf).

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/nscf/eigenplot_qe.png)

#### 1.3.2.5. Projected Density of States (PDOS) calculation
The PDOS calculation is used to determine how localized a state is. The input file must be set up as follows:
```bash
&PROJWFC
  prefix = 'diamond_pd',
  outdir = '../tmp/',
  filpdos= 'diamond_pd_pdos.dat',
  DeltaE = 0.02,
  Emax = 50,
  Emin = -50,
  degauss = 0.007,
  ngauss = 0,
  lsym = .TRUE.,
/
```
Once the calculation is done, information about the orbitals with the largest contributions to each state can be obtained for each band and spin channel using the [qe_loc.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_loc.py) script. Furthermore, the Localization factor diagram can be plotted using the [qe_locplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_locplot.py) script. In this last script, the VBM and CBM values must always be entered manually.

An example for NV-3 can be found in the [pdos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/pdos).

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/pdos/eigenplot_localization.png)


#### 1.3.2.6. Electronic charge density
This calculation can be performed by setting up the input file as follows:
```bash
&INPUTPP
    prefix='diamond_pd'
    outdir='../tmp'
    plot_num=0
/
&PLOT
    iflag=3
    output_format=5
    fileout='diamond_pd_chg_3d.xsf'
/
```
An example for NV-3 can be found in the [chg_3d folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/chg_3d). The 3D charge density can be visualized using the [VESTA](https://jp-minerals.org/vesta/en/download.html) software along with the [diamond_pd_chg_3d.xsf](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/chg_3d/diamond_pd_chg_3d.xsf) file.

#### 1.3.2.7. Electrostatic Potential
This calculation can be performed by setting up the input file as follows:
```bash
&INPUTPP
    prefix='diamond_pd'
    outdir='../tmp'
    plot_num=11
/
&PLOT
    iflag=3
    output_format=6
    fileout='diamond_v_elec_defect.cube'
/
```
This calculation will be important because it will help us compute the energy corrections. An example for NV-3 can be found in the [potential folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/NV-3/potential).

### 1.3.3. Finite-Size Correction
The main artifact of the supercell approach for point-defect calculations consists in the introduction of periodic images of the defect located in the simulation cell. Such periodically-repeated array of defects corresponds to very high defect concentrations for commonly used supercell types. In such case, defect-defect interactions are large and can considerably affect the predicted formation energy of the point defect. Among the kinds of defect-defect interactions, electrostatic ones are never negligible for any practical supercell size. The study of point defects in the dilute limit then requires some scheme to correct for such spurious electrostatic interactions.

<p align="center">
  <img src="https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Figures/finite-size-correction.png" alt="Descripción de la imagen">
</p>

As mentioned previously, the output information from the **potential calculation** is relevant for computing the energy corrections. In addition, the **dielectric constant** is also required for this calculation. The **dielectric constant** can be computed by following the steps described in the [phonons folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons). To compute these energy corrections, the [sxdefectalign](https://sxrepo.mpie.de/projects/sphinx-add-ons/files) software will be used.

**NV center in diamond:** For our example, the information has been processing in the [Finite_Size_correction folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Supercell-PD/Calculations/PBE/defect/Finite_Size_correction). The following energy corrections were obtained:

<div align="center">
  
| Charge State | Energy Correction (meV) |
|:------------:| :----------------------:|
|   -3         |       1400.70           | 
|   -2         |       535.632           |
|   -1         |       54.2815           |
|    0         |           0.0           |
|   +1         |       297.506           |
|   +2         |       1053.18           |

</div>

### 1.3.4. Formation energy diagram
Then, to gather important information such as the chemical potentials, total energies, charge states, energy of the valence band maximum, and energy corrections, the formation energy diagram can be plotted. 

**NV center in diamond:** For our example, information such as the chemical potentials, total energies, charge states, and energy of the valence band maximum has been computed. However, energy corrections have not yet been included.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Figures/formation_energy.png)

Including the energy corrections:

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Supercell-PD/Figures/formation_energy-corrections.png)

---
# 2. HSE06 functional
---
The steps for calculations using hybrid functionals are the same as those outlined for calculations using PBE functionals.
