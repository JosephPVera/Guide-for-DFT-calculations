# Steps for Quantum ESPRESSO calculations: Phonons

Steps for Quantum ESPRESSO calculations using **PBE** functional. Native phonon calculations in Quantum ESPRESSO are not implemented for hybrid functionals: https://www.quantum-espresso.org/Doc/ph_user_guide/node7.html.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 0. Workflow
![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/Figures/phon_qe_workflow.png)

## 1. Relaxation
The aim of the relaxation calculation is to find the most stable arrangement of atoms by minimizing total energy, reducing internal forces to zero, and optimizing cell geometry. The calculation is performed in the same way as described in section **1.3. Relaxation** in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive).

## 2. Self-Consistent Field (SCF) calculation
The aim of this calculation is to get the converged charge density and wavefunctions of the unperturbed system. The calculation is performed in the same way as described in section **1.4. Self-Consistent Field (SCF) calculation** in the [primitive folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/Primitive). 

An example for diamond is also included in the [scf folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/scf).

## 3. Dynamic Matrix (DM) calculation
Quantum ESPRESSO uses **Density-Functional Perturbation Theory (DFPT)** via the **ph.x** code to compute the dynamical matrix and phonon properties without needing supercells. By evaluating the second derivatives of the total energy with respect to atomic displacements, DFPT efficiently yields the interatomic force constants and vibrational frequencies for specific **q**-vectors. Therefore, the aim of this calculation is to compute the first-order change in the potential and wavefunctions for a chosen wavevector **q**, generating the dynamical matrix elements.

> **NOTE:** Instead of physically moving an atom and repeating a complete ground-state calculation for every possible displacement, DFPT calculates the response mathematically for an infinitesimally small disturbance (linear-response calculation, **linear** because the displacement is considered infinitesimally small). When an atom moves, the electrons rearrange, and this changes the forces acting on all the atoms around it. The calculation determines these changes in force and therefore learns how strongly the atoms interact when they vibrate. It does this for different wavelengths and directions of vibration throughout the crystal's reciprocal space. The main result is information describing the vibrational behavior of the crystal at those sampled points.

This type of calculation can be performed by setting up the input file as follows:
```bash
&INPUTPH
  outdir = '../tmp/'
  prefix = 'diamond'
  tr2_ph = 1d-14
  ldisp = .true.
  epsil = .true.
!  recover = .true.
  nq1 = 6
  nq2 = 6
  nq3 = 6
  fildyn = 'diamond.dyn'
/
```
The meaning of each tag is described in the [HP Input Description](https://www.quantum-espresso.org/Doc/INPUT_HP.html). The input file can be executed using the following command:
```bash
ph.x -inp dyn-matrix_ph.in > dyn-matrix_ph.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 ph.x -inp dyn-matrix_ph.in > dyn-matrix_ph.out
```
where **20** represents the number of CPU cores used for the calculation. Once the calculation is done, several **.dyn** files will be created. In addition, the electronic dielectric tensor can also be extracted from the **.out** file.

An example of this calculation for diamond can be found in the [ph folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/ph). The **electronic dielectric tensor** can be extract using the [qe_dielectric.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_dielectric.py) script. The extracted information looks as follows:
```bash
          Dielectric constant in cartesian axis 

          (       5.895297868      -0.007680884      -0.007680884 )
          (      -0.007680884       5.895297868       0.007680884 )
          (      -0.007680884       0.007680884       5.895297868 )
```

## 4. Diagonalization of the DM calculation
This step is a post-processing calculation in which the DM is diagonalized to obtain the phonon frequencies and eigenvectors, which are then used, together with the Born effective charges and the electronic dielectric tensor, to calculate the total contribution to the dielectric tensor and, consequently, the **ionic dielectric tensor**. This type of calculation can be performed by setting up the input file as follows:
```bash
&INPUT
  fildyn = 'diamond.dyn1'
  asr = 'crystal'
  lperm = .true.
/
```
The meaning of each tag is described in the [DYNMAT Input Description](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html). The input file can be executed using the following command:
```bash
dynmat.x -inp dyn-matrix_dynmat.in > dyn-matrix_dynmat.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 dynmat.x -inp dyn-matrix_dynmat.in > dyn-matrix_dynmat.out
```
where **20** represents the number of CPU cores used for the calculation. Keep in mind that **.dyn1** file, which contents information at $$\Gamma$$-point, must be copied from the **ph folder**:
```bash
cp -r ../ph/diamond.dyn1 .
```
Once the calculation is done, the electronic and total dielectric tensor can also be extracted from the **.out** file:
```bash
Electronic dielectric permittivity tensor (relative, adimensional)
         5.895298   -0.007681   -0.007681
        -0.007681    5.895298    0.007681
        -0.007681    0.007681    5.895298
 
 ... with zone-center polar mode contributions
         5.895298   -0.007681   -0.007681
        -0.007681    5.895298    0.007681
        -0.007681    0.007681    5.895298
```
Since that:

$$
\epsilon _{o} = \epsilon _{\inf} + \epsilon _{ion}
$$

Therefore:

$$
\epsilon _{ion} = 
\begin{pmatrix}
5.895298 & -0.007681 & -0.007681 \\
-0.007681 & 5.895298 & 0.007681 \\
-0.007681 & 0.007681 & 5.895298
\end{pmatrix}
-
\begin{pmatrix}
5.895298 & -0.007681 & -0.007681 \\
-0.007681 & 5.895298 & 0.007681 \\
-0.007681 & 0.007681 & 5.895298
\end{pmatrix}
$$

## 5. Inverse Fourier Transform of the DM calculation 
Transform the dynamical matrices from a uniform **q**-mesh into real-space Interatomic Force Constants (IFCs). The **ph.x** calculation gives information in reciprocal space, but we want to know something more intuitive: how does one atom affect another atom when it moves?. **q2r.x** performs a Fourier transformation of the dynamical matrices and produces the real-space IFCs.

> **NOTE:** This calculation takes the vibrational information obtained at different points in reciprocal space (from the previous calculation) and converts it into a real-space description of the interactions between atoms. Conceptually, it changes the question from "how does the crystal respond to a vibration with this particular wavelength?" to "how does the force on one atom change when another atom moves?" The result is a collection of force constants describing the strength of interactions between atoms at different positions in the crystal. This step is essentially a change of representation: the physical information from the phonon calculation is reorganized into a form that describes the crystal's local atomic interactions.

This type of calculation can be performed by setting up the input file as follows:
```bash
&INPUT
  fildyn = 'diamond.dyn'
  zasr = 'crystal'
  flfrc = 'diamond.fc'
/
```
The meaning of each tag is described in the [Q2R Input Description](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html). Before running the input, the files with the **.dyn** extension must be copied to this folder as follows:
```bash
cp -r ../ph/diamond.dyn* .
```
Now, run the input file using the following command:
```bash
q2r.x -inp dyn-matrix_q2r.in > dyn-matrix_q2r.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 q2r.x -inp dyn-matrix_q2r.in > dyn-matrix_q2r.out
```
where **20** represents the number of CPU cores used for the calculation. An example of this calculation for diamond can be found in the [q2r folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/q2r). This calculation will generate a **dimond.fc** file.

## 6. Fourier Transformation of the real space calculation 
Perform an inverse Fourier transform back to any arbitrary **q**-point to plot phonon dispersions or calculate density of states (DOS). Now we have the real-space force constants, so **matdyn.x** can calculate phonons at whatever q-points we want. At each point along the high-symmetry path, **matdyn.x** constructs the dynamical matrix and solves an eigenvalue problem.

> **NOTE:** This calculation uses those real-space atomic interactions to determine the vibrational modes at any wavevector you are interested in. This is important because the previous calculation only explicitly sampled a finite grid of points. Once the real-space force constants are known, the program can reconstruct the vibrational behavior at new points without performing another expensive DFPT calculation at every one of them. You therefore specify a path through reciprocal space, usually passing through important high-symmetry points, and the program calculates the possible vibrational frequencies along that path.

This type of calculation can be performed by setting up the input file as follows:
```bash
&INPUT
  asr = 'crystal'
  flfrc = 'diamond.fc'
  flfrq = 'diamond.freq'
  flvec = 'diamond.modes'
!  loto_2d = .true.
  loto_disable = .false.
  q_in_band_form = .true.
  q_in_cryst_coord = .true.
/
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
0.3750 0.3750 0.7500   1  !K
```
The meaning of each tag is described in the [MATDYN Input Description](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html). Before running the input, the file with the **.fc** extension must be copied to this folder as follows:
```bash
cp -r ../q2r/diamond.fc .
```
Now, run the input file using the following command:
```bash
matdyn.x -inp dyn-matrix_matdyn.in > dyn-matrix_matdyn.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 matdyn.x -inp dyn-matrix_matdyn.in > dyn-matrix_matdyn.out
```
where **20** represents the number of CPU cores used for the calculation. 

🔔**Reminder:** This calculation already includes the LO–TO splitting, which is useful for polar materials, via **loto_disable = .false.**. This phenomenon typically occurs at the $\Gamma$-point.

An example of this calculation for diamond can be found in the [matdyn folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/matdyn).

## 7. Phonon Dispersion Relation (Band Structure) calculation
The resulting phonon dispersion tells you how the allowed vibrational frequencies change with the wavelength and direction of the vibration. This diagram can be plotted using the output from the previous calculation, which is available in the [matdyn folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/matdyn). The [qe_phonband.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_phonband.py) script allows you to plot the phonon band structure:

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/matdyn/phonon_band-1.png)

Since diamond contains two atoms in the primitive cell, and each atom has three degrees of freedom, there should be six branches in the phonon band structure. These can be plotted separately using the **--split** tag.

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/matdyn/phonon_band.png)

## 8. Density Of States (DOS) calculation
A phonon DOS calculation counts the number of available vibrational modes at each frequency. This type of calculation can be performed by setting up the input file as follows:
```bash
&INPUT
  asr   = 'crystal'
  flfrc = 'diamond.fc'
  flfrq = 'diamond.dos.freq'
  flvec = 'diamond.dos.modes'
  dos   = .true.
  fldos = 'diamond.dos'
  nk1   = 25
  nk2   = 25
  nk3   = 25
/
```
Before running the input, the file with the .fc extension must be copied to this folder as follows: 
```bash
cp -r ../q2r/diamond.fc .
```
Now, run the input file using the following command:
```bash
matdyn.x -inp phon_dos.in > phon_dos.out
```
Alternatively, the input file can be executed using parallelization:
```bash
mpirun -np 20 matdyn.x -inp phon_dos.in > phon_dos.out
```
where **20** represents the number of CPU cores used for the calculation. An example of this calculation for diamond can be found in the [dos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/dos). The [qe_phondos.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_phondos.py) script allows you to plot the phonon DOS:

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/dos/diamond_dos.png)

## 9. Projected Density Of States (PDOS) calculation
A phonon PDOS calculation breaks down the vibrations to show the specific contributions of individual atoms (projects the total vibrational modes onto individual atoms). This plot can be obtained using the output from the previous calculation, which is available in the [dos folder](https://github.com/JosephPVera/Guide-for-DFT-calculations/tree/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/dos). The [qe_phondos.py](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/Scripts/qe_phondos.py) script, together with the **--pdos** tag, allows you to plot the phonon PDOS:

![Alt text](https://github.com/JosephPVera/Guide-for-DFT-calculations/blob/main/Quantum-ESPRESSO/phonons/phon_QE/Calculations/dos/diamond_pdos.png)
