---

# Steps for VASP calculations: Phonons
Check [phonopy](https://phonopy.github.io/phonopy/) and [phonopy-vasp](https://phonopy.github.io/phonopy/vasp.html).

The outputs can be used for custom plots using [phonplot.py](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/phonplot.py).

---
## 0. Creating the tree
```bash
mkdir phonon relax
mkdir phonon/nac
```
---

## 1. Activation
1. Identify for the module
   ```bash
   module spider phonopy
2. Load the module
   ```bash
   module load phonopy/2.16.3-foss-2022a
3. Create the folders  
   ```bash
   mkdir relax phonon

## 2. Relaxation
In **relax** folder:
1. Create **INCAR_relax** file, example:
   ```bash
   # Electronic relaxation
   ALGO   = Normal    # Algorithm for electronic relaxation
   NELMIN = 4         # Minimum # of electronic steps
   NELM = 100         # sets the maximum number of electronic self-consistency steps 
   EDIFF  = 1E-8      # Accuracy for electronic groundstate
   ENCUT  = 500       # Cut-off energy for plane wave expansion
   PREC   = Accurate  # Low/Normal/Accurate
   LREAL  = .FALSE.   # Projection in reciprocal space
   ISMEAR = 1         # Smearing of partial occupancies
   SIGMA  = 0.1       # Smearing width
   ISPIN  = 2         # Spin polarization
   ISTART = 0         # Determines whether or not to read the WAVECAR
   ICHARG = 2         # Determines how VASP constructs the initial charge density

   # Ionic relaxation
   EDIFFG = -0.0005   # Defines the break condition for the ionic relaxation loop
   NSW    = 200       # Static high-accuracy calculation without relaxation
   IBRION = 2         # Algorithm for relaxing atomic positions 
   ISIF = 3           # 3 means relax volume, ISIF 2 or 0 relaxes only atoms, not lattice vectors
   ISYM = 1           # Determines the way VASP treats symmetry
   LWAVE = .FALSE.    # Determines whether the wavefunctions are saved in WAVECAR
   LCHARG = .FALSE.   # Determines whether the charge densities are saved in CHGCAR and CHG
   LMAXMIX = 4
 
   # Memory handling
   NPAR    = 4        # number of bands that are treated in parallel
   NCORE = 10         # number of compute cores that work on an individual orbital
   ```
2. Introduce the **POSCAR** and **jobfile** (HPC clusters use Slurm as workload manager and job scheduler).
3. Create **KPOINTS** file using command
   ```bash
   kmesh.py
   ```
4. Create **POTCAR** using comand
   ```bash
   makepot . Pt
   ```
5. For run your work use the following command
   ```bash
   sub 
   ```   
8. Check if your work is finished
   ```bash
   st 
   ```   

## 3. Phonon
In **phonon** folder:
1. Create **INCAR_phonon** file, example:
   ```bash
   # Electronic relaxation
   ALGO   = Normal    # Algorithm for electronic relaxation
   NELMIN = 4         # Minimum # of electronic steps
   NELM = 100         # sets the maximum number of electronic self-consistency steps 
   EDIFF  = 1E-8      # Accuracy for electronic groundstate
   ENCUT  = 500       # Cut-off energy for plane wave expansion
   PREC   = Accurate  # Low/Normal/Accurate
   LREAL  = .FALSE.   # Projection in reciprocal space?
   ISMEAR = 1         # Smearing of partial occupancies
   SIGMA  = 0.1       # Smearing width
   ISTART = 0         # Determines whether or not to read the WAVECAR
   ICHARG = 2         # Determines how VASP constructs the initial charge density

   # Ionic relaxation
   NSW    = 0         # Static high-accuracy calculation without relaxation
   IBRION = -1        # Algorithm for relaxing atomic positions 
   ISYM = 0           # Determines the way VASP treats symmetry
   LWAVE = .FALSE.    # Determines whether the wavefunctions are saved in WAVECAR
   LCHARG = .FALSE.   # Determines whether the charge densities are saved in CHGCAR and CHG
   LMAXMIX = 4
 
   # Memory handling
   NPAR    = 4        # number of bands that are treated in parallel
   NCORE = 10         # number of compute cores that work on an individual orbital
   ``` 
2. Use the **CONTCAR** file from Relaxation section (**relax folder**) and change the name to **POSCAR**.
   ```bash
   cp ../relax/CONTCAR POSCAR
   ``` 
3. Copy **KPOINTS** and **POTCAR** from Relaxation section (**relax folder**).
   ```bash
   cp ../relax/KPOINTS KPOINTS
   cp ../relax/POTCAR POTCAR
   ``` 
4. Use the command
   ```bash
   phonopy -d --dim="2 2 2"
   ```
   for apply the transformation and create
   different **POSCAR's** with finite-difference (displaced atoms) in the lattice parameter
   (Supercell method). It is possible to change the values "2 2 2" according to your material.
5. Now you will find **POSCAR's** with different numbers: **POSCAR-001**, **POSCAR-002** and so on.
6. Create folders for each new **POSCAR** with 
   ```bash
   mkdir dis-001 dis-002
   ```
7. For each folder, for example **dis-001** folder:
   - Copy **POSCAR-001** and change the name to **POSCAR**
     ```bash
     cp POSCAR-001 dis-001/POSCAR
     ```
   - Copy **INCAR_phonon**, **KPOINTS**, **POTCAR** and **jobfile**
     ```bash
     cp INCAR_phonon dis-001/INCAR
     cp KPOINTS POTCAR jobfile dis-001
     ```
   - Run your work
     ```bash
     sub 
     ```  
   - Repeat the same steps for the other cases
8. Now use the command 
   ```bash
   cd ..
   phonopy -f dis-001/vasprun.xml dis-002/vasprun.xml
   ```
   for create the **FORCE_SETS** file (this file is very important).


**IMPORTANT: NEXT CALCULATIONS PERFORM IN PHONON FOLDER**
### 3.1. Density of states (DOS)
1. Create **mesh.conf** file 
   ```bash
   touch mesh.conf
   ```
   Include name of the atoms of your material with the tag **ATOM_NAME**, the transformation applied with the tag **DIM**  
   and the Monkhorst-Pack scheme with the tag **MP**. Here an example:
   ```bash
   ATOM_NAME = B N 
   DIM = 2 2 2
   MP = 8 8 8
   ```
2. Use the following command for plot the DOS
   ```bash
   phonopy -p -s mesh.conf
   ```
3. Check the outcome 
   ```bash
   evince total_dos.pdf
   ```
4. Check information in **total_dos.dat** file.

### 3.2. Thermal properties
1. Use the following command for plot the thermal properties
   ```bash
   phonopy -p -s -t  mesh.conf > thermal.dat
   ```
2. Check the outcome 
   ```bash
   evince thermal_properties.pdf
   ```
3. Check information in **thermal_properties.yaml** or **thermal.dat** file.

### 3.3. Partial Density of States (PDOS)
1. Create **pdos.conf** file
   ```bash
   touch pdos.conf
   ```
   Include name of the atoms of your material with the tag **ATOM_NAME**, the transformation applied with the tag **DIM** ,
   the Monkhorst-Pack scheme with the tag **MP** and the Projected DOS with the tag **PDOS**. Here an example:
   ```bash
   ATOM_NAME = B N
   DIM = 2 2 2
   MP = 8 8 8
   PDOS = AUTO
   ```
2. Use the following command for plot the PDOS
   ```bash
   phonopy -p -s pdos.conf
   ```
3. Check the outcome 
   ```bash
   evince partial_dos.pdf
   ```
4. Check information in **projected_dos.dat** file.

### 3.4. Band structure
1. Create **band.conf** file
   ```bash
   touch band.conf
   ```   
   Include name of the atoms of your material with the tag **ATOM_NAME**, the transformation applied with the tag **DIM**,
   the high symmetry points with the tag **BAND** and the labels for the high symmetry points with the tag **BAND_LABELS**. Here an example:
   ```bash
   ATOM_NAME = B N
   DIM =  2 2 2
   BAND= 0.0 0.0 0.0   0.5 0.0 0.5   0.5 0.25 0.75   0.375 0.375 0.75   0.0 0.0 0.0   0.5 0.5 0.5   0.625 0.250 0.625   0.5 0.25 0.75   0.5 0.5 0.5  0.375 0.375 0.75,   0.625 0.25 0.625   0.5 0.0 0.5
   BAND_LABELS = $\Gamma$ X W K $\Gamma$ L U W L K:U X    
   ```     
2. Use the following command for plot the band structure
   ```bash
   phonopy -p -s band.conf
   ```
3. Save the information in .dat file, the second line is the path
   ```bash
   phonopy-bandplot --gnuplot band.yaml > band.dat
   ```
4. Check the outcome
   ```bash
   evince band.pdf
   ```    
5. Check information in **band.yaml** and **band.dat** file.

### 3.4. Non-analytical term correction (NAC)
0. Create a **nac** file
   ```bash
   mkdir nac
   cd ..
   ```
1. Create **INCAR_nac**, example:
   ```bash
   # Electronic relaxation
   ALGO   = Normal        # Algorithm for electronic relaxation
   PREC = Accurate        # Low/Normal/Accurate
   IBRION = 8            # Algorithm for relaxing atomic positions 
   NELMIN = 5             # sets the maximum number of electronic self-consistency steps
   ENCUT = 500            # Cut-off energy for plane wave expansion
   EDIFF  = 1E-8          # Accuracy for electronic groundstate
   ISMEAR = 0             # Smearing of partial occupancies.
   SIGMA = 1E-02          # Smearing width
   IALGO = 38             # selects the algorithm to optimize the orbitals. 
   LREAL = .FALSE.        # Projection in reciprocal space?
   LWAVE = .FALSE.        # Determines whether the wavefunctions are saved in WAVECAR
   LCHARG = .FALSE.       # Determines whether the charge densities are saved in CHGCAR and CHG
   LEPSILON = .TRUE.      # determines the static dielectric matrix, ion-clamped piezoelectric tensor and the Born effective charges using density functional perturbation theory
   ```
2. Copy **POSCAR (primitice cell)**, **KPOINTS**, **POTCAR** and **jobfile**
   ```bash
   cp ../POSCAR ../jobfile ../KPOINTS ../POTCAR .
   ``` 
3. Run your work
   ```bash
   sub 
   ```  
4. Use the following command for create the **BORN** file
   ```bash
   phonopy-vasp-born > BORN 
   ```
5. Check the dielectric tensor with [dielectric.py](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/dielectric.py)
   ```bash
   dielectric.py 
   ```
### 3.5. Correcting calculations with [NAC](https://phonopy.github.io/phonopy/formulation.html#non-analytical-term-correction-theory)   
1. Now copy BORN file to **phonon** folder
   ```bash
   cp BORN ../
   ```   
2. Repeat the above commands adding the tag **--nac** for calculate with the term correction
   - DOS:                
     ```bash
     phonopy -p -s --nac mesh.conf
     ```
   - Thermal properties: 
     ```bash
     phonopy -p -s -t --nac mesh.conf > thermal.dat
     ```
   - PDOS:               
     ```bash
     phonopy -p -s --nac pdos.conf
     ```
   - Band Structure:    
     ```bash
     phonopy -p -s --nac band.conf
     phonopy-bandplot --gnuplot band.yaml > band.dat
     ```
3. For plot DOS and Band Structure at once
   - Create **band-dos.conf**, here an example:
     ```bash
     ATOM_NAME = B N
     DIM =  2 2 2
     MP = 8 8 8
     BAND= 0.0 0.0 0.0   0.5 0.0 0.5   0.5 0.25 0.75   0.375 0.375 0.75   0.0 0.0 0.0   0.5 0.5 0.5   0.625 0.250 0.625   0.5 0.25 0.75   0.5 0.5 0.5  0.375 0.375 0.75,   0.625 0.25 0.625   0.5 0.0 0.5
     BAND_LABELS = $\Gamma$ X W K $\Gamma$ L U W L K:U X
     ```
   - Use the following command for plot
     ```bash
     phonopy -p -s --nac band-pdos.conf
     ```
   - Check the outcome 
     ```bash
     evince band_dos.pdf
     ```

### 3.6. Dielectric constant
1. Check the **BORN** file (second line is information about the electronic dielectric tensor), here an example:
   ```bash
   # epsilon and Z* of atoms 1 3
      4.46664232    0.00000000    0.00000000    0.00000000    4.46664232    0.00000000    0.00000000    0.00000000    4.68631509 
      2.51940463    0.00000000    0.00000000    0.00000000    2.51940463    0.00000000    0.00000000    0.00000000    2.67878546 
     -2.51940463   -0.00000000    0.00000000   -0.00000000   -2.51940463   -0.00000000    0.00000000    0.00000000   -2.67878546 
   ```

---
# Reminder
1. Plots without NAC need the following files:
   - DOS: **FORCE_SETS**, **POSCAR** (primitive cell) and **mesh.conf**
   - Thermal: **FORCE_SETS**, **POSCAR** (primitive cell) and **mesh.conf**
   - PDOS: **FORCE_SETS**, **POSCAR** (primitive cell) and **pdos.conf**
   - Band structure: **FORCE_SETS**, **POSCAR** (primitive cell) and **band.conf**
   - Band structure and PDOS at once: **FORCE_SETS**, **POSCAR** (primitive cell) and **band-pdos.conf**
2. Plots with NAC need the same files that without NAC by adding the **NAC** file.
---
# Enjoy your outcomes
---
# Disfruta tus resultados
---

