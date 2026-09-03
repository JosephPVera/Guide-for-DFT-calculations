#!/usr/bin/env python
# Written by Joseph P.Vera
# 2024-10

"Code to create the KPOINTS file for HSE06 calculations (path for band structure), using the OUTCAR and KPOINTS files from the band structure \
and the IBZKPT file from DOS with the PBE calculation"

# Read the OUTCAR file and extract the information 
with open('../../PBE/bs/OUTCAR') as infile, open('kpoints.dat', 'w') as outfile:
    copy = False
    for line in infile:
        if line.strip() == "k-points in reciprocal lattice and weights: k-points along fcc high symmetry lines":
            copy = True
        if copy:
            outfile.write(line)
        if line.strip() == "":
            copy = False
            
# Clean kpoints.dat, remove the fourth column for add the zeros column
with open("kpoints.dat", "r+") as fil:
    file1 = fil.readlines()
    fil.seek(0)
    for line in file1:
        if "k-points" not in line:
            if not line.isspace():
                fil.write(line)
    fil.truncate()
    
# Format kpoints.dat
with open("kpoints.dat", 'r+') as fopen:
    string = ""
    for line in fopen.readlines():
        string = string + line[:-5] + "\n"  

with open("kpoints.dat", 'w') as fopen:
    fopen.write(string)

# Read the KPOINTS file, get the labels
kpoints_dict = {}
with open('../../PBE/bs/KPOINTS', 'r') as kpoints_file:
    for line in kpoints_file:
        # Ignore lines that do not contain k-point data
        if line.strip() and not line.startswith("k-points") and not line.startswith("#") and not line.startswith("Line-mode") and not line.startswith("reciprocal"):
            parts = line.split()
            # Ignore lines that have less than 4 parts or contain a non-numeric character
            if len(parts) >= 4 and all(part.replace('.', '', 1).isdigit() for part in parts[:3]):  
                position = tuple(round(float(coord), 8) for coord in parts[:3])  # Take the first three as position 
                label = parts[3]  # corresponding label
                # Save only if the position is not already in the dictionary
                if position not in kpoints_dict:
                    kpoints_dict[position] = label  # Save in the dictionary

# Read kpoints.dat and add corresponding labels
with open("kpoints.dat", 'r+') as fopen:
    lines = fopen.readlines()
    fopen.seek(0)
    
    last_label = None  
    for line in lines:
        line_stripped = line.strip()
        if line_stripped:  # Check that the line is not empty
            # removing unnecessary zeros
            position = tuple(round(float(coord), 8) for coord in line_stripped.split()[:3])
            
            # Write the original line
            if position in kpoints_dict:
                current_label = kpoints_dict[position]
                # Only write the label if it is not the same as the previous one
                if current_label != last_label:
                    fopen.write(f"{line_stripped} {current_label}\n") 
                    last_label = current_label  # Update the last label
                else:
                    fopen.write(f"{line_stripped}\n")  
            else:
                fopen.write(f"{line_stripped}\n")  

    fopen.truncate()  

# Clean IBZKPT, remove the "Tetrahedra" section
with open('../dos/IBZKPT', 'r') as ibzkpt_file:
    lines = ibzkpt_file.readlines()

# Remove lines starting from "Tetrahedra"
cleaned_lines = []
for line in lines:
    if "Tetrahedra" in line:
        break  
    cleaned_lines.append(line)

# Concatenate cleaned IBZKPT with kpoints.dat in KPOINTS file
with open('KPOINTS', 'w') as output_file:
   output_file.writelines(cleaned_lines)  
   with open('kpoints.dat', 'r') as kpoints_data_file:
      # Read the lines from kpoints.dat and add 3 spaces at the beginning
      for kpoint_line in kpoints_data_file:
          output_file.write('   ' + kpoint_line) 

# Count lines in KPOINTS file and modify the second line
with open('KPOINTS', 'r+') as output_file:
    lines = output_file.readlines()
    line_count = len(lines)  # Count the number of lines
    
    # Replace the value in the second line with line_count - 3
    if len(lines) > 1:
        lines[1] = str(line_count - 3) + "\n"  # Replace with the new value

    # Write modified lines
    output_file.seek(0)  # Go back to the start of the file
    output_file.writelines(lines)
    output_file.truncate()  # Ensure the file has the correct size

print("The files were saved")
