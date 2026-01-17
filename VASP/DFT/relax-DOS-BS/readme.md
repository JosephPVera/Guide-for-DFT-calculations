--- 
# Steps for VASP calculations: Relax, DOS and Band Structure
Check [VASP - UIO](https://wiki.uio.no/mn/kjemi/vaspwiki/index.php/Main_Page).

Steps for VASP calculations using **PBE** and **HSE06** pseudopotentials.

Useful scripts [**forces.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/forces.py), [**bandgap.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/bandgap.py), [**toten.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/toten.py), [**kmesh.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/kmesh.py), **makepot**, [**dospo.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/dospo.py) and [**band.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/band.py). 
Check **/.../vasp/template/bin**.

---
# 0. Creating the tree 
   ```bash
   mkdir encut kdensity PBE HSE06
   mkdir encut/perfect encut/increased encut/decreased
   mkdir kdensity/perfect kdensity/increased kdensity/decreased
   mkdir PBE/relax PBE/dos PBE/bs
   mkdir HSE06/relax HSE06/dos HSE06/bs
   ```
---

---
# 1. PBE functional
---
## 1.1. Convergence test
The first step in performing this analysis is to create different configurations using a initial configuration. To do this, we first define our perfect configuration (**POSCAR_perfect**) and then create the perturbed configurations by modifying their lattice constants with a variation of **$\Delta a$** (**POSCAR_increased** and **POSCAR_decreased**). This is motivated by the fact that relative energies are more significant than total energies.

### 1.1.1. Energy Cutoff
1. Enter to **encut** folder
   ```bash
   cd encut
   ```
2. Create different folders in each of the **perfect**, **increased** and **decreased** folders
   ```bash
   mkdir perfect/{200..950..50}
   mkdir increased/{200..950..50}
   mkdir decreased/{200..950..50}
   ```
   and then copy each **POSCAR** into its respective folder
   ```bash
   for i in {200..950..50}; do cp POSCAR_perfect "perfect/$i/POSCAR"; done
   for i in {200..950..50}; do cp POSCAR_increased "increased/$i/POSCAR"; done
   for i in {200..950..50}; do cp POSCAR_decreased "decreased/$i/POSCAR"; done
   ```
3. Enter the missing folders in each **{200..950..50}** folder
   - Create the same **jobfile** file in each folder.
   - Create the **INCAR** file and change the **ENCUT** tag following the name of the folders: **{200..950..50}**
   - Create **KPOINTS** files in each folder using the command
     ```bash
     kmesh.py
     ```
     or at once, using:
     ```bash
     for dir in */;do cd $dir; kmesh.py; cd ../;done
     ```
   - Create **POTCAR** file using the comand 
     ```bash
     makepot . Pt
     ```
     change the element **Pt** according to your material. If you have two elements in the material use
     ```bash
     makepot . Pt Si
     ```
     or all at once, using:
     ```bash
     for dir in */;do cd $dir; makepot . Pt Si; cd ../;done
     ```
     This is just a concatenation of the pseudopotential files. 
4. Use the following command for run your calculations
   ```bash
   sub
   ```
   or all at once, using
   ```bash
   for dir in */;do cd $dir; sub; cd ../;done 
   ```   
5. Use the following command for check if your calculations are finished
   ```bash
   st
   ```   
6. If all calculations are finished, use the following commands for check your outcomes 
   ```bash
   tot.py */vasprun.xml
   forces.py */OUTCAR
   ```
   **tot,py** script allows us to check information about total energy, while **forces.py** script allows us to check information about MxForce, Drift, and pressure.
7. Save your outcomes in a file with differents extension like .ods, .dat, .xlsx or .txt using the
   commands
   ```bash
   tot.py */OUTCAR > toten.dat
   forces.py */OUTCAR > vaspout.dat
   ```   
8. **OPTIONAL**: Once the calculations are completed, **Relative energies versus Energy cutoff** can be plotted straight using [**encut.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/encut.py).

### 1.1.2. k-density
1. Enter to **kdensity** folder
   ```bash
   cd k-density
   ```
2. Create different folders in each of the **perfect**, **increased** and **decreased** folders
   ```bash
   mkdir perfect/{2..9..1}
   mkdir increased/{2..9..1}
   mkdir decreased/{2..9..1}
   ```
   and then copy each **POSCAR** into its respective folder
   ```bash
   for i in {2..9..1}; do cp POSCAR_perfect "perfect/$i/POSCAR"; done
   for i in {2..9..1}; do cp POSCAR_increased "increased/$i/POSCAR"; done
   for i in {2..9..1}; do cp POSCAR_decreased "decreased/$i/POSCAR"; done
   
3. Enter the missing folders in each **{2..9..1}** folder
   - Create the same **POTCAR** and **jobfile** files in each folder or simply copy them from **Convergence test (Energy Cutoff) section**.
   - Use the **INCAR** file with the converged energy cutoff, from **Convergence test (Energy Cutoff) section**, in each folder.
   - Create **KPOINTS** file in each folder by changing the **k-density** tag following the name of the files: **{2..9..1}**, use the command
     ```bash
     kmesh.py --d 2
     ```
     change the last number for different k-density. All at once, using:
     ```bash
     for dir in {2..9}; do cd "$dir"; kmesh.py -d "$dir";cd ..;done
     ```
     check if it is correct
     ```bash
     grep k-density */KPOINTS
     ```
4. Run your calculations.
5. Check if your calculations are finished.
6. Repeat the steps 6 and 7 from **Convergence test (Energy Cutoff) section**.
7. **OPTIONAL**: Once the calculations are completed, **Relative energies versus k-density** can be plotted straight using [**kdensity.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/kdensity.py).

## 1.2. Relaxation
1. Enter to **relax** folder
   ```bash
   cd PBE/relax
   ```
2. Create **INCAR_PBE_relax** file, use the converged energy cutoff **ENCUT** (following the convergence test) for the next calculations.
3. Use the same **POSCAR**, **POTCAR** and **jobfile** from Convergence test section.
4. Create **KPOINTS** file following the converged k-density.   
5. Run your work.
6. Check your outcomes.

## 1.3. Density of states (DOS)
0. This is a self-consistent calculation
1. Enter to **dos** folder
   ```bash
   cd ../dos
   ```
2. Create **INCAR_PBE_dos** file
3. Use the **CONTCAR** file from Relaxation section and change the name to **POSCAR**
   ```bash
   cp ../relax/CONTCAR POSCAR
   ```
4. Use the same **jobfile**, **KPOINTS** and **POTCAR** files from Relaxation section
   ```bash
   cp ../relax/jobfile ../relax/KPOINTS ../relax/POTCAR .
   ```
5. Run your work
6. Check your outcomes, using the following command you can check the information about 
   the bandgap (VBM and CBM)
   ```bash
   bandgap OUTCAR
   ```
7. Use the following script for plot the DOS
   ```bash
   dospo.py
   ```
8. It is possible check the Local density of states (LDOS) using the command    
   ```bash
   dospo.py 1 --all
   ```
   change the last number according to your material.
9. Check your images 
   ```bash
   eog total_dos.png
   ```

## 1.4. Band structure
0. This is a non-self-consistent calculation
1. Enter to **bs** folder
   ```bash
   cd ../bs
   ```
2. Create **INCAR_PBE_bs** file, include the new tag **ICHARG = 11**, last tag indicates the 
   non-self-consistent calculation
3. Copy **CHGCAR**, **POSCAR**, **POTCAR** and **jobfile** from DOS section
   ```bash
   cp ../dos/CHGCAR ../dos/POSCAR ../dos/jobfile ../dos/POTCAR .
   ```
4. Create **KPOINTS** file with the high symmetry points for the First Brillouin Zone (1BZ) [[1]](https://doi.org/10.1016/j.commatsci.2010.05.010), here an example
   ```bash
   k-points along fcc high symmetry lines
   20     0  !                           # of points per line
   Line-mode
   reciprocal
   0.000  0.000  0.000  \Gamma
   0.500  0.000  0.500  X

   0.500  0.000  0.500  X
   0.500  0.250  0.750  W

   0.500  0.250  0.750  W
   0.375  0.375  0.750  K

   0.375  0.375  0.750  K
   0.000  0.000  0.000  \Gamma

   0.000  0.000  0.000  \Gamma
   0.500  0.500  0.500  L
 
   0.500  0.500  0.500  L
   0.625  0.250  0.625  U

   0.625  0.250  0.625  U
   0.500  0.250  0.750  W

   0.500  0.250  0.750  W
   0.500  0.500  0.500  L

   0.500  0.500  0.500  L
   0.375  0.375  0.750  K

   0.375  0.375  0.750  K
   0.625  0.250  0.625  U

   0.625  0.250  0.625  U
   0.500  0.000  0.500  X
   ```
5. Run your work
6. Plot the band structure with the script
   ```bash
   band.py
   ```
7. Check your image 
   ```bash
   eog band_structure_plot.png
   ```

---
# 2. HSE06 functional
---

## 2.1. Relaxation
1. Enter to **relax** folder
   ```bash
   cd HSE06/relax
   ```
2. Create **INCAR_HSE06_relax** file, include the tags for hybrid calculations:
   ```bash
   LHFCALC = .TRUE.        # specifies whether a Hartree-Fock/DFT hybrid functional type calculation is performed. 
   HFSCREEN = 0.2          # HF Screening parameter (0.2 for HSE06)
   AEXX = 0.25             # Fraction of exact exchange in a Hartree-Fock-type/hybrid-functional calculation
   Time = 0.4              # Timestep (0.4 for HSE06)
   ```
3. Introduce **POSCAR**, **KPOINTS**, **POTCAR** and **jobfile**, which can be copied from PBE calculations
   ```bash
   cp ../../PBE/dos/POSCAR ../../PBE/dos/KPOINTS ../../PBE/dos/POTCAR ../../PBE/dos/jobfile .
   ```
4. Run your work.
5. Check your outcomes.

## 2.2. Density of states (DOS)
0. This is a self-consistent calculation.
1. Enter to **dos** folder
   ```bash
   cd ../dos
   ```
2. Create the **INCAR_HSE06_dos** file, include the tags for hybrid calculations.
3. Use the **CONTCAR** file from Relaxation_HSE06 section and change the name to **POSCAR**
   ```bash
   cp ../relax/CONTCAR POSCAR
   ```
4. Copy KPOINTS, POTCAR, jobfile from Relaxation_HSE06 section
   ```bash
   cp ../relax/jobfile ../relax/KPOINTS ../relax/POTCAR .
   ```
5. Run your work.
6. Use the same steps 6, 7, 8 and 9 from DOS_PBE section.

## 2.3. Band structure
0. This is a non-self-consistent calculation
1. Enter to **bs** folder
   ```bash
   cd ../bs
   ```
2. Create **INCAR_HSE06_bs**, include the tags for hybrid calculations and a new tag **ICHARG = 11**, last tag indicates the 
   non-self-consistent calculation.
3. Copy **CHGCAR**, **POTCAR**, **POSCAR** and **jobfile** from DOS_HSE06 section
   ```bash
   cp ../dos/CHGCAR ../dos/POSCAR ../dos/jobfile ../dos/POTCAR .
   ```
4. Create **KPOINTS** file
   - Copy **IBZKPT** file from DOS_HSE06 section
     ```bash
     cp ../dos/IBZKPT .
     ```
   - Copy **OUTCAR** file from **Band structure PBE section**: inside **OUTCAR_PBE** look for the
     "**k-points in reciprocal lattice and weights: k-points**" section (it is information with 4
     columns) and copy it (**copy only the numbers**)
     ```bash
     cp ../../PBE/bs/OUTCAR OUTCAR_PBE
     ```
     Here is a brief example of **OUTCAR_PBE**:
     ```bash
     k-points in reciprocal lattice and weights: k-points along fcc high symmetry lines  
     0.00000000  0.00000000  0.00000000       0.005
     0.02631579  0.00000000  0.02631579       0.005
     0.05263158  0.00000000  0.05263158       0.005
     0.07894737  0.00000000  0.07894737       0.005
     0.10526316  0.00000000  0.10526316       0.005
     0.13157895  0.00000000  0.13157895       0.005
     0.15789474  0.00000000  0.15789474       0.005
     0.18421053  0.00000000  0.18421053       0.005
     0.21052632  0.00000000  0.21052632       0.005
     ```
   - **Here it is possible to use two methods**:
     1. Create **kdensity.dat** file and paste the "**k-points in reciprocal lattice and weights: 
        k-points**" information
        ```bash
        touch kdensity.dat
        ```
        then concatenate with **IBZKPT** file to create the **KPOINTS** file using the command
        ```bash
        cat IBZKPT kpoints.dat > KPOINTS
        ```
     2. Manually add the "**k-points in reciprocal lattice and weights: 
        k-points**" information at the final of **IBZKPT** file without leaving spaces, then change the name from **IBZKPT** to
        **KPOINTS** file.
        ```bash
        mv IBZKPT KPOINTS
        ```
   - Enter to **KPOINTS** file
     ```bash
     vim KPOINTS
     ```
     and **change the weights to zero (only in the pasted part)**, it is the 4th
     column. Here is a brief example:
     ```bash
     0.00000000  0.00000000  0.00000000       0
     0.02631579  0.00000000  0.02631579       0
     0.05263158  0.00000000  0.05263158       0
     0.07894737  0.00000000  0.07894737       0
     0.10526316  0.00000000  0.10526316       0
     0.13157895  0.00000000  0.13157895       0
     0.15789474  0.00000000  0.15789474       0
     0.18421053  0.00000000  0.18421053       0
     0.21052632  0.00000000  0.21052632       0     
     ```
   - In **KPOINTS** file change the number of points (second line), usually it is the number of lines in 
     the file minus 3 (Ln - 3).
   - Include the high symmetry points for the 1BZ, look for the points in pasted part and include
     the labels after the weights.
   - **OPTIONAL**: The [**kpoints.py**](https://github.com/JosephPVera/DFT-calculations/blob/main/DFT/scripts/kpoints.py) script create the **KPOINTS** file using the previous steps.
5. Run your work
6. Plot the band structure.
7. Check your image.


---
# Enjoy your outcomes
---
# Disfruta tus resultados
---
