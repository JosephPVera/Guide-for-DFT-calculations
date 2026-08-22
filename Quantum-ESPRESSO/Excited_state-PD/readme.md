# Steps for Quantum ESPRESSO calculations: Excited States

Steps for Quantum ESPRESSO calculations using **PBE** and **HSE06** functionals.

A guide to installing quantum ESPRESSO can be found in the [Quantum ESPRESSO repository](https://github.com/JosephPVera/Quantum_espresso_software).

## 1. Delta Self-Consistent Field (ΔSCF) method
Exited states can also be studied in Quantum ESPRESSO using the Delta Self-Consistent Field ($\Delta$SCF) method. This method allows electrons to be promoted from an occupied energy level to an unoccupied one by specifying the occupations.

Within the Franck-Condon approximation, the electronic excitation is much faster than the nuclear motion. Thus, 
ΔSCF can be used for calculating excited-state properties such as vertical absorption (VAE) and vertical emission energy (VEE). Furthermore, this method can be used to calculate the zero-phonon lines (ZPL) by performing a full atomic relaxation in the excited-state configuration and thus account for the Stockes shifts. This method is commonly used for calculating the optical properties of point defects in semiconductors and insulators

## 2. Zero Phonon Line (ZPL) calculation
![Alt text]()


