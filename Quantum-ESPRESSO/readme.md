--- 
# Steps for Quantum ESPRESSO calculations: Relax, DOS, PDOS, Band Structure, and Charge Density

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** pseudopotentials.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

---
# 1. PBE functional
---

## 1.1. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Figures/QE_workflow_pbe.png)

## 1.2. Convergence tests
The first step in obtaining accurate results is to perform convergence tests for parameters such as the **energy cutoff for wavefunctions**, **energy cutoff for charge density**, and **k-point mesh**. These parameters can be modified through the **ecutwfc** and **ecutrho** tags, as well as the **K_POINTS** section.  

### 1.2.1. Energy cutoff for wavefunctions
Create several folders named according to the energy cutoff values to be used. For example:
```bash
mkdir {10..80..5}
```
Then, create the **.in** file for the system under study. Next, copy the **.in** file into each of the created folders, modifying the **ecutwfc** tag to match the energy cutoff value indicated by the corresponding folder name. For example, a **diamond.in** file can be used for a diamond calculation, as shown below:
```bash
&CONTROL
  calculation = 'scf',
  prefix      = 'diamond',
  outdir      = './tmp/',
  pseudo_dir  = '../../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  disk_io = 'nowf',
/

&SYSTEM
  ibrav =  2,
  celldm(1) = 6.74,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 10.0,
  nbnd = 8,
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF
  
ATOMIC_POSITIONS (alat)
C 0.00 0.00 0.00
C 0.25 0.25 0.25

K_POINTS (automatic)
10 10 10 0 0 0
```
The meaning of each tag is described in the [PWscf Input Description](https://www.quantum-espresso.org/Doc/INPUT_PW.html). The input file can be executed using the following command:
```bash
pw.x -i diamond.in > diamond.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 pw.x -inp diamond.in > diamond.out
```
where **20** represents the number of CPU cores used for the calculation. An example of these calculations can be found in the [ecutwfc folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/convergence/ecutwfc). As a result of the convergence analysis, it is possible to plot a convergence curve, as shown below:
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/PBE/convergence/ecutwfc/delta_e_encut.png)

The total energy from each calculation can be extracted using the [qe_tot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_tot.py) script.

### 1.2.2. Energy cutoff for charge density
Once an **ecutwfc** value has been selected (for the diamond example, **ecutwfc = 45.0**), the next step is to perform the convergence test for the **energy cutoff for charge density** using the **ecutrho** tag. We must to create several folders named according to the **ecutrho** values to be used. For example:
```bash
mkdir {1..15..1}
```
**Note:** Keep in mind that, in this case, **ecutrho = Nx(ecutwfc)** is being considered.

Now, create the **.in** files, keeping **ecutwfc = 45.0** fixed and modifiying the **ecutrho** tag to match the energy cutoff value indicated by the corresponding folder name. For example, the previous input file (**diamond.in**) will be modified as shown in the next section:
```bash
&SYSTEM
  ibrav =  2,
  celldm(1) = 6.74,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 90.0,
  nbnd = 8,
/
```
An example of these calculations can be found in the [ecutrho folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/convergence/ecutrho). As a result of the convergence analysis, it is possible to plot a convergence curve, as shown below:
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/PBE/convergence/ecutrho/delta_e_ecutrho.png)

⚠️ **WARNING**: **ecutrho** values less than or equal to **ecutwfc** values are not allowed. In case you try to run them, the following error will be encountered:
```bash
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     task #         5
     from set_cutoff : error #         1
     ecutrho <= ecutwfc?!?
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
```
Check an example in [ecutrho error](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/convergence/ecutrho/1).

### 1.2.3. K-point mesh
Now, **ecutwfc** and **ecutrho** values has been selected (for the diamond example, **ecutwfc = 45.0** and **ecutrho = 180.0**), the final step is to perform the convergence test for the **k-point mesh** using the **K_POINTS** section. We must to create several folders named according to the **k-point grid** values to be used. For example:
```bash
mkdir {1..15..1}
```
**Note:** Keep in mind that, in this case, the **k-point grid** is represented as **kxkxk**.

Create the **.in** files, keeping **ecutwfc = 45.0** and **ecutrho = 180.0** fixed and modifiying the **K_POINTS** section to match the grid value indicated by the corresponding folder name. For example, the previous input file (**diamond.in**) will be modified as shown in the next section:
```bash
K_POINTS (automatic)
10 10 10 0 0 0
```
An example of these calculations can be found in the [kpoints folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/convergence/kpoints). As a result of the convergence analysis, it is possible to plot a convergence curve, as shown below:
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/PBE/convergence/kpoints/delta_e_kpoint.png)

## 1.3. Relaxation
The aim of the relaxation calculation is to find the most stable arrangement of atoms by minimizing total energy, reducing internal forces to zero, and optimizing cell geometry. This type of calculation can be performed by setting up the input file as follows:
```bash
&CONTROL
  calculation = 'vc-relax',
  prefix      = 'diamond',
  outdir      = './tmp/',
  pseudo_dir  = '../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  disk_io = 'nowf',
/

&SYSTEM
  ibrav =  2,
  celldm(1) = 6.74,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  nbnd = 8,
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

&IONS
/

&CELL
  cell_dofree='all'
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF
  
ATOMIC_POSITIONS (alat)
C 0.00 0.00 0.00
C 0.25 0.25 0.25

K_POINTS (automatic)
8 8 8 0 0 0
```
Keep in mind that, for this and all subsequent calculations, the converged values of **ecutwfc**, **ecutrho**, and **k-point mesh** should be kept fixed. For the diamond calculation, use the converged values **ecutwfc = 45.0**, **ecutrho = 180.0**, and **K_POINTS = 8 8 8** for all subsequent calculations.

After running the calculation, it is important to extract the lattice parameters of the relaxed system. This can be done using the [qe_lattice.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_lattice.py) script. For our example, the diamond calculation, this information can be found in the [relax folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/relax). The lattice parameters of the relaxed system are as follows:
```bash
CELL_PARAMETERS (alat=  6.74000000)
  -0.500778093   0.000000000   0.500778093
  -0.000000000   0.500778093   0.500778093
  -0.500778093   0.500778093   0.000000000

ATOMIC_POSITIONS (alat)
C               -0.0000000000       -0.0000000000       -0.0000000000
C                0.2503890466        0.2503890466        0.2503890466
End final coordinates
```
The input file can be executed using the following command:
```bash
pw.x -i diamond_relax.in > diamond_relax.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 pw.x -inp diamond_relax.in > diamond_relax.out
```
where **20** represents the number of CPU cores used for the calculation. In addition, the crystal structure can be visualized using the [xcrysden](http://www.xcrysden.org/) or [ASE](https://docs.ase-lib.org/) software. Since [VESTA](https://jp-minerals.org/vesta/en/download.html) software can not read **.in** files, a convenient option is to use the [qe_convert.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_convert.py) script to convert the **.in** file into a **POSCAR** file, which can then be opened in VESTA.

## 1.4. Self-Consistent Field (SCF) calculation
The aim of the SCF calculation is to solve the Kohn-Sham equations iteratively to find the ground-state electron charge density, total energy, and converged electronic wavefunctions for a system at fixed atomic positions. At this point, the lattice parameters obtained from the **relaxation calculation** must be used. This type of calculation can be performed by setting up the input file as follows:
```bash
&CONTROL
  calculation = 'scf',
  prefix      = 'diamond',
  outdir      = '../tmp/',
  pseudo_dir  = '../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  restart_mode = 'from_scratch',
  disk_io = 'low',
/

&SYSTEM
  ibrav =  0,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  nbnd = 8,
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 200,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF

K_POINTS (automatic)
8 8 8 0 0 0
  
CELL_PARAMETERS (angstrom)
  -1.786102785   0.000000000   1.786102785
  -0.000000000   1.786102785   1.786102785
  -1.786102785   1.786102785   0.000000000

ATOMIC_POSITIONS (crystal)
C  -0.0000000000       -0.0000000000       -0.0000000000
C   0.2503890466        0.2503890466        0.2503890466
```
An example of this calculation can be found in the [scf folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/properties/scf). The total energy and band gap can be extracted using the [qe_tot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_tot.py) and [qe_gap.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_gap.py) scripts.

The input file can be executed using the following command:
```bash
pw.x -i diamond_scf.in > diamond_scf.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 pw.x -inp diamond_scf.in > diamond_scf.out
```
where **20** represents the number of CPU cores used for the calculation.

## 1.5. Non-Self-Consistent Field (NSCF) calculation
The aim of the NSCF calculation is to compute accurate electronic eigenvalues on a denser reciprocal space (k-point) grid. For this calculation, the **calculation** tag and **K_POINTS** section are modified from the previous input file, as follows:
```bash
&CONTROL
  calculation = 'nscf',
  prefix      = 'diamond',
  outdir      = '../tmp/',
  pseudo_dir  = '../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  restart_mode = 'from_scratch',
  disk_io = 'low',
/
```
```bash
K_POINTS (automatic)
24 24 24 0 0 0
```
An example of this calculation can be found in the [nscf folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/properties/nscf). The true band gap can be extracted using the [qe_gap.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_gap.py) script.

The input file can be executed using the following command:
```bash
pw.x -i diamond_nscf.in > diamond_nscf.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 pw.x -inp diamond_nscf.in > diamond_nscf.out
```
where **20** represents the number of CPU cores used for the calculation.

## 1.6. Density Of States (DOS) calculation
The aim of the DOS calculation is to find the number of available electronic energy states per unit energy interval in a material. This type of calculation can be performed by setting up the input file as follows:
```bash
&DOS
  prefix = 'diamond',
  outdir = '../tmp/',
  fildos = 'diamond_dos.dat',
  DeltaE = 0.02,
  Emax = 50,
  Emin = -50,
  degauss = 0.007,
  ngauss = 0,
/
```
The meaning of each tag is described in the [DOS Input Description](https://www.quantum-espresso.org/Doc/INPUT_DOS.html). An example of this calculation can be found in the [dos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/properties/dos). The input file can be executed using the following command:
```bash
dos.x -i diamond_dos.in > diamond_dos.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 dos.x -inp diamond_dos.in > diamond_dos.out
```
where **20** represents the number of CPU cores used for the calculation. In addition, the DOS can be plotted using the [dos.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/dos.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/PBE/properties/dos/diamond_dos.png)

## 1.7. Projected Density Of States (PDOS) calculation
The aim of the PDOS calculation is to break down the total density of states (DOS) into specific atomic and orbital contributions. It reveals which atoms and angular momentum channels (s, p, d, f, and so on) dominate bonding, hybridization, and the states near the Fermi level. This type of calculation can be performed by setting up the input file as follows:
```bash
&PROJWFC
  prefix = 'diamond',
  outdir = '../tmp/',
  filpdos= 'diamond_pdos.dat',
  DeltaE = 0.02,
  Emax = 50,
  Emin = -50,
  degauss = 0.007,
  ngauss = 0,
  lsym = .TRUE.,
/
```
The meaning of each tag is described in the [PDOS Input Description](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html). An example of this calculation can be found in the [pdos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/properties/pdos). The input file can be executed using the following command:
```bash
projwfc.x -i diamond_projwfc.in > diamond_projwfc.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 projwfc.x -inp diamond_projwfc.in > diamond_projwfc.out
```
where **20** represents the number of CPU cores used for the calculation. In addition, the PDOS corresponding to the contribution of each atom can be plotted using the [pdos.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/pdos.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/PBE/properties/pdos/diamond_pdos-C-atom_1.png)

## 1.8. Band structure calculation
The aim of the band structure calculation is to determine allowed electron energy levels along high-symmetry paths in reciprocal space, identifying whether a material is a metal, semiconductor, or insulator, and finding its fundamental band gap. This type of calculation can be performed by setting up the input file as follows:

### 1.8.1. Bands calculation
This step calculates the eigenvalues (Kohn–Sham energies) at specific k-points defined along the high-symmetry points of the First Brillouin zone, using the fixed potential. This type of calculation can be performed by setting up the input file as follows:
```bash
&CONTROL
  calculation = 'bands',
  prefix      = 'diamond',
  outdir      = '../tmp/',
  pseudo_dir  = '../../pseudos/',
  verbosity = 'high',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  restart_mode = 'restart',
  disk_io = 'low',
/

&SYSTEM
  ibrav =  0,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  nbnd = 8,
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 200,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF

K_POINTS {crystal_b}
10
  0.0000 0.0000 0.0000 200  !G
  0.5000 0.0000 0.5000 200  !X
  0.5000 0.2500 0.7500 200  !W
  0.3750 0.3750 0.7500 200  !K
  0.0000 0.0000 0.0000 200  !G
  0.5000 0.5000 0.5000 200  !L
  0.6250 0.2500 0.6250 200  !U
  0.5000 0.2500 0.7500 200  !W
  0.5000 0.5000 0.5000 200  !L
  0.3750 0.3750 0.7500   0  !K
  
CELL_PARAMETERS (angstrom)
  -1.786102785   0.000000000   1.786102785
  -0.000000000   1.786102785   1.786102785
  -1.786102785   1.786102785   0.000000000

ATOMIC_POSITIONS (crystal)
C  -0.0000000000       -0.0000000000       -0.0000000000
C   0.2503890466        0.2503890466        0.2503890466
```
An example of this calculation can be found in the [band folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/properties/band). The input file can be executed using the following command:
```bash
pw.x -i diamond_bands.in > diamond_bands.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 pw.x -inp diamond_bands.in > diamond_bands.out
```
where **20** represents the number of CPU cores used for the calculation.

### 1.8.2. Post-processing of bands calculation
This step generates clean, readable text files containing energy values versus k-distance, which can be used to plot the band structure diagram. This type of calculation can be performed by setting up the input file as follows:
```bash
&BANDS
  prefix = 'diamond'
  outdir = '../tmp/'
  filband = 'diamond_bands.dat'
/
```
The meaning of each tag is described in the [BANDS Input Description](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html). An example of this calculation can be found in the [band_pp folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/properties/band_pp). The input file can be executed using the following command:
```bash
bands.x -i diamond_bands_pp.in > diamond_bands_pp.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 bands.x -inp diamond_bands_pp.in > diamond_bands_pp.out
```
where **20** represents the number of CPU cores used for the calculation. In addition, the band structure diagram can be plotted using the [bandplot.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/bandplot.py) script.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/PBE/properties/band_pp/diamond_bands.png)

## 1.9. Electronic charge density
The aim of the charge density extraction is to convert raw, internal binary electronic data into a readable, spatial 3D grid format. This type of calculation can be performed by setting up the input file as follows:
```bash
&INPUTPP
    prefix='diamond'
    outdir='../tmp'
    plot_num=0
/
&PLOT
    iflag=3
    output_format=5
    fileout='diamond_chg_3d.xsf'
/
```
The meaning of each tag is described in the [PP Input Description](https://www.quantum-espresso.org/Doc/INPUT_PP.html). An example of this calculation can be found in the [chg_3d folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/PBE/properties/chg_3d). The input file can be executed using the following command:
```bash
pp.x -i diamond_chg_3d.in > diamond_chg_3d.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 pp.x -inp diamond_chg_3d.in > diamond_chg_3d.out
```
where **20** represents the number of CPU cores used for the calculation. In addition, the 3D charge density can be visualized using the [VESTA](https://jp-minerals.org/vesta/en/download.html) software along with the [diamond_chg_3d.xsf](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/PBE/properties/chg_3d/diamond_chg_3d.xsf) file.

# 2. HSE06 functional
## 2.1. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Figures/QE_workflow_hse06.png)

## 2.2. Convergence tests
### 2.2.1. From convergence tests with PBE functional
The initial parameters for the subsequent calculations will be taken from the previous calculations, i.e., those performed using the PBE functional. Furthermore, the relaxed structure obtained using the PBE functional will be used as the initial structure for the subsequent calculations. For the diamond example, the converged values **ecutwfc = 45.0**, **ecutrho = 180.0**, and **K_POINTS = 8 8 8** will be used.

### 2.2.2. Q-point mesh
Since **ecutwfc**, **ecutrho**, and **K_POINTS** values has been selected; the final step is to perform the convergence test for the **q-point mesh** using the **nqx1**, **nqx2**, and **nqx3** tags. We must to create several folders named according to the **q-point grid** values to be used. For example:
```bash
mkdir {1..9..1}
```
**Note:** Keep in mind that, in this case, the **q-point grid** is represented as **qxqxq**.

Create the **.in** files, keeping **ecutwfc**, **ecutrho**, and **k-point mesh** fixed and modifiying the **nqx1**, **nqx2**, and **nqx3** tags to match the grid value indicated by the corresponding folder name. For example, the input file (**diamond.in**) will be modified as shown in the next section:
```bash
&CONTROL
  calculation = 'scf',
  prefix      = 'diamond-HSE06',
  outdir      = './tmp/',
  pseudo_dir  = '../pseudos/',
  verbosity = 'low',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  restart_mode = 'from_scratch',
  disk_io = 'nowf',
/

&SYSTEM
  ibrav =  0,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  nbnd = 8,
  input_dft='hse',
  exx_fraction = 0.25,
  screening_parameter = 0.2, 
  nqx1 = 3, nqx2 = 3, nqx3 = 3, 
  x_gamma_extrapolation = .true.,
  exxdiv_treatment = 'gygi-baldereschi',
  nosym = .true.
  noinv = .true.
/

&ELECTRONS
  conv_thr = 1.0d-8,
  electron_maxstep = 200,
  mixing_beta = 0.7,
  mixing_mode = 'plain',
  scf_must_converge = .TRUE.,
  startingwfc = 'random',
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-n-kjpaw_psl.1.0.0.UPF

K_POINTS (automatic)
8 8 8 0 0 0
  
CELL_PARAMETERS (angstrom)
  -1.786102785   0.000000000   1.786102785
  -0.000000000   1.786102785   1.786102785
  -1.786102785   1.786102785   0.000000000

ATOMIC_POSITIONS (crystal)
C  -0.0000000000       -0.0000000000       -0.0000000000
C   0.2503890466        0.2503890466        0.2503890466
```
An example of these calculations can be found in the [q-points folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/HSE06/convergence/q-points). As a result of the convergence analysis, it is possible to plot a convergence curve, as shown below:

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Calculations/HSE06/convergence/q-points/bandgap.png)

The plateauing pattern is typical of the q-point mesh convergence and indicates that the q-point mesh should be chosen using divisors of the k-point mesh. This behavior can be observed in the previous figure. For the diamond calculation, since **k = 8**, the q-point mesh should be chosen using its divisors, namely **q = 1, 2, 4**, and **8**. However, for this example, we have chosen to use **q = 3**, i.e., a **3x3x3** q-point mesh.

## 2.3. Relaxation
At this point, all the parameters have been chosen: **ecutwfc**, **ecutrho**, **k-point mesh**, and **q-point mesh**. This type of calculation can be performed by setting up the input file as follows:
```bash
&CONTROL
  calculation = 'vc-relax',
  prefix      = 'diamond-HSE06',
  outdir      = './tmp/',
  pseudo_dir  = '../pseudos/',
  verbosity = 'low',
  tprnfor = .true.,
  tstress = .true.,
  forc_conv_thr = 1.0d-6,
  etot_conv_thr = 1.0d-8,
  disk_io = 'nowf',
/

&SYSTEM
  ibrav =  0,
  nat  = 2,
  ntyp = 1,
  ecutwfc = 45.0,
  ecutrho = 180.0,
  nbnd = 8,
  input_dft='hse',
  exx_fraction = 0.25,
  screening_parameter = 0.2, 
  nqx1 = 2, nqx2 = 2, nqx3 = 2, 
  x_gamma_extrapolation = .true.,
  exxdiv_treatment = 'gygi-baldereschi',
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

&IONS
/

&CELL
  cell_dofree='all'
/

ATOMIC_SPECIES
  C  12.0107 C.pbe-nc.UPF

K_POINTS (automatic)
8 8 8 0 0 0

CELL_PARAMETERS (angstrom)
  -1.786102785   0.000000000   1.786102785
  -0.000000000   1.786102785   1.786102785
  -1.786102785   1.786102785   0.000000000

ATOMIC_POSITIONS (crystal)
C  -0.0000000000       -0.0000000000       -0.0000000000
C   0.2503890466        0.2503890466        0.2503890466
```
⚠️ **WARNING**: This type of calculation does not work when using Ultrasoft (US) pseudopotentials or Projector-Augmented Wave (PAW) datasets because the forces for that combination are not implemented. This calculation can only be performed using Norm-Conserving (NC) pseudopotentials. If you attempt to run a calculation using either of these pseudopotential types, the following error message will be displayed:
```bash
```
After running the calculation, it is important to extract the lattice parameters of the relaxed system. This can be done using the [qe_lattice.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_lattice.py) script. For our example, the diamond calculation, this information can be found in the [relax folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Calculations/HSE06/relax).
