#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-11

"Code for search information about the dielectric tensor"

import xml.etree.ElementTree as ET

file_path = 'vasprun.xml'

tree = ET.parse(file_path)
root = tree.getroot()

epsilon_ion = root.find(".//varray[@name='epsilon_ion']") # keyword to ionic tensor <varray name="epsilon_ion" >

if epsilon_ion is not None:
    print("Ionic dielectric tensor:")
    for vector in epsilon_ion.findall("v"):
        print(vector.text)
else:
    print("The ionic dielectric tensor was not found in the vasprun.xml file.")


epsilon = root.find(".//varray[@name='epsilon']") # keyword to electronic tensor <varray name="epsilon" >

if epsilon is not None:
    print("\nElectronic dielectric tensor:")
    for vector in epsilon.findall("v"):
        print(vector.text)
else:
    print("The electronic dielectric tensor was not found in the vasprun.xml file.")
