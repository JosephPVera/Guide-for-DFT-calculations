# The script belongs to Pydefect Package https://kumagai-group.github.io/pydefect/tutorial.html, here modifications were only made for academic uses.
# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
import re
from typing import Dict, Any
from pymatgen.core import Element

# define how the names are process. path: /home/joseph/.local/lib/python3.12/site-packages/pydefect/util
def remove_digits(name: str) -> str:
    """ "O1" -> "O" """
    return ''.join([i for i in name if not i.isdigit()])

def only_digits(name: str) -> str:
    """ "O1" -> "1" """
    return ''.join([i for i in name if i.isdigit()])

elements = [str(e) for e in Element]
e_va = elements + ["Va"]
e_i = elements + ["i"]

def defect_mpl_name(name: str) -> str:
    """ 
    Converts:
    'Va_O1-C_N2' -> '$\\rm V_{{\\rm O}1}\\rm C_{{\\rm N}2}$'
    """
    parts = name.split("-")
    formatted_parts = []

    for part in parts:
        in_name, out_name = part.split("_")

        # Format in_name
        if in_name in elements:
            in_name = f"\\rm {in_name}"
        elif in_name == "Va":
            in_name = "\\rm V"
        else:
            in_name = f"\\rm {in_name}"

        # Format out_name
        r_out_name = remove_digits(out_name)
        d_out_name = only_digits(out_name)
        out_name = f"{{\\rm {r_out_name}}}{d_out_name}"

        formatted_parts.append(f"{in_name}_{{{out_name}}}")

    return "$" + "".join(formatted_parts) + "$" ### option: "-"

def typical_defect_name(name: str) -> bool:
    parts = name.split("-")
    for part in parts:
        x = part.split("_")
        if len(x) != 2:
            return False
        _in, _out = x
        if not (_in in e_va and remove_digits(_out) in e_i):
            return False
    return True

def prettify_names(d: Dict[str, Any], style) -> Dict[str, Any]:
    result = {}
    out_names = []
    for name in d.keys():
        out_names.extend([part.split("_")[1] for part in name.split("-")])

    for name, v in d.items():
        parts = []
        for part in name.split("-"):
            in_name, out_name = part.split("_")
            r_out_name = remove_digits(out_name)
            out_name = r_out_name if f"{r_out_name}2" not in out_names else out_name
            parts.append("_".join([in_name, out_name]))

        _name = "-".join(parts)

        if _name in result:
            raise ValueError("The prettified names are conflicted. "
                             "Change the defect names, please.")
        if style is None:
            pass
        elif style == "mpl":
            _name = defect_mpl_name(_name)
        else:
            raise ValueError(f"Style {style} is not adequate. Set mpl or None.")
        result[_name] = v
    return result
