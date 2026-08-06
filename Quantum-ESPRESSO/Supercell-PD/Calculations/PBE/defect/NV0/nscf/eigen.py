#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

#!/usr/bin/env python3
"""
plot_bands_spin.py
-------------------
Lee un archivo .out de Quantum ESPRESSO (calculo spin-polarizado),
extrae los bloques SPIN UP / SPIN DOWN, y para cada k-point extrae
las energias de banda (eV) y sus numeros de ocupacion asociados.

Regla de graficado (scatter, x = indice de k-point, y = energia eV):
    occ > 0.9            -> azul
    occ < 0.1             -> rojo
    0.1 <= occ <= 0.9      -> verde

Parametros VBM/CBM/RES (siempre se deben definir VBM y CBM):
    RES controla el reescalamiento de las energias graficadas y, junto con
    ello, donde se dibuja el sombreado de banda de valencia (azul) / banda
    de conduccion (roja). Se controla con el flag --res:
        - sin --res  -> RES = 0.0 (no reescala energias). Sombreado: azul
                         hasta y=VBM, rojo desde y=CBM
        - con --res  -> RES = VBM (reescala energias, E-VBM). Sombreado:
                         azul hasta y=0, rojo desde y=CBM-VBM
    En general, el sombreado siempre queda en:
        - azul: de y=(VBM-RES) hacia abajo
        - rojo: de y=(CBM-RES) hacia arriba

Configuracion:
    Edita las variables INPUT_FILE, OUTPUT_FILE, VBM y CBM al inicio de este
    script (seccion "CONFIGURACION MANUAL") y luego simplemente ejecuta:

        python plot_bands_spin.py

    Si dejas INPUT_FILE = None, el script busca automaticamente un archivo
    .out en la carpeta actual, ignorando los logs tipo slurm-1234.out.

    Usa --index para imprimir el band index (empezando en 1) al costado de
    cada punto graficado (si varios estan superpuestos o separados por
    <= 0.1 eV, se agrupan en una lista, ej. "12, 13, 14, 15"):

        python plot_bands_spin.py --index

    Usa --res para reescalar las energias respecto al VBM (RES = VBM). Sin
    este flag, RES = 0.0 (no se reescala):

        python plot_bands_spin.py --res
"""

import os
import re
import glob
import argparse
import matplotlib.pyplot as plt


# =====================================================================
# CONFIGURACION MANUAL - edita estos valores segun tu caso
# =====================================================================
INPUT_FILE = None               # ruta a tu archivo .out, o None para buscar
                                 # automaticamente el .out en la carpeta actual
                                 # (ignorando archivos tipo slurm-1234.out)
OUTPUT_FILE = "eigenplot_qe.png"  # nombre del PNG de salida

VBM = 12.82469624   # valor del VBM (eV) -- SIEMPRE se debe definir
CBM = 18.08184593    # valor del CBM (eV) -- SIEMPRE se debe definir
# =====================================================================


FLOAT_RE = re.compile(r"[-+]?\d+\.\d+")
KPOINT_HEADER_RE = re.compile(
    r"k\s*=\s*([-+0-9.\s]+?)\(\s*(\d+)\s*PWs\)\s*bands\s*\(ev\):", re.IGNORECASE
)


def extract_floats(line):
    """Devuelve la lista de numeros flotantes encontrados en una linea."""
    return [float(x) for x in FLOAT_RE.findall(line)]


def find_out_file(folder="."):
    """
    Busca automaticamente un archivo .out en 'folder', ignorando los archivos
    de log de slurm tipo slurm-1234.out (chequeado solo por el nombre).
    """
    all_out_files = glob.glob(os.path.join(folder, "*.out"))

    # Exclude files like slurm-0001.out, slurm-5768.out, etc. (checked by filename only)
    out_files = [f for f in all_out_files if not re.match(r"^slurm-\d+\.out$", os.path.basename(f))]

    if not out_files:
        raise FileNotFoundError(
            "No se encontro ningun archivo .out valido en la carpeta "
            "(se ignoran los archivos tipo slurm-*.out)."
        )
    if len(out_files) > 1:
        print(f"Aviso: se encontraron varios archivos .out {sorted(out_files)}, usando: {out_files[0]}")

    return out_files[0]


def split_spin_sections(text):
    """
    Divide el archivo en la seccion SPIN UP y SPIN DOWN.
    Si no existen esos marcadores (calculo no polarizado), devuelve
    todo el contenido como una unica seccion 'UP'.
    """
    up_marker = re.search(r"-+\s*SPIN\s+UP\s*-+", text, re.IGNORECASE)
    down_marker = re.search(r"-+\s*SPIN\s+DOWN\s*-+", text, re.IGNORECASE)

    if up_marker and down_marker:
        up_text = text[up_marker.end():down_marker.start()]
        down_text = text[down_marker.end():]
        # cortar SPIN DOWN si aparece otro marcador tipo "SPIN UP" luego (multiples ciclos scf)
        next_up = re.search(r"-+\s*SPIN\s+UP\s*-+", down_text, re.IGNORECASE)
        if next_up:
            down_text = down_text[: next_up.start()]
        return {"UP": up_text, "DOWN": down_text}
    else:
        return {"UP": text, "DOWN": ""}


def parse_section(section_text):
    """
    Parsea una seccion (UP o DOWN) y devuelve una lista de k-points, cada
    uno con sus energias y ocupaciones:
        [ {"k": (kx,ky,kz), "energies": [...], "occupations": [...]}, ... ]
    """
    kpoints = []

    # localizar todas las cabeceras "k = ... bands (ev):"
    headers = list(KPOINT_HEADER_RE.finditer(section_text))
    if not headers:
        return kpoints

    for i, h in enumerate(headers):
        kvec_str = h.group(1).split()
        try:
            kvec = tuple(float(v) for v in kvec_str[:3])
        except ValueError:
            kvec = (None, None, None)

        block_start = h.end()
        block_end = headers[i + 1].start() if i + 1 < len(headers) else len(section_text)
        block_text = section_text[block_start:block_end]

        # separar energias (antes de "occupation numbers") de ocupaciones (despues)
        occ_split = re.split(r"occupation numbers", block_text, flags=re.IGNORECASE)
        energy_text = occ_split[0]
        occ_text = occ_split[1] if len(occ_split) > 1 else ""

        energies = []
        for line in energy_text.splitlines():
            if line.strip() == "" or set(line.strip()) <= {"."}:
                continue
            energies.extend(extract_floats(line))

        occupations = []
        for line in occ_text.splitlines():
            if line.strip() == "" or set(line.strip()) <= {"."}:
                continue
            occupations.extend(extract_floats(line))

        if energies:
            # si por algun motivo no hay ocupaciones (raro), rellenar con NaN
            if not occupations:
                occupations = [float("nan")] * len(energies)
            # recortar/emparejar por si difieren en longitud
            n = min(len(energies), len(occupations))
            kpoints.append(
                {
                    "k": kvec,
                    "energies": energies[:n],
                    "occupations": occupations[:n],
                }
            )

    return kpoints


def color_for_occupation(occ):
    if occ != occ:  # NaN check
        return "gray"
    if occ > 0.9:
        return "blue"
    elif occ < 0.1:
        return "red"
    else:
        return "green"


def plot_spin_channel(ax, kpoints, title, vbm, cbm, res=0, show_index=False, show_ylabel=True):
    if not kpoints:
        ax.set_title(f"{title} (sin datos)")
        return []

    shift = res
    n_k = len(kpoints)

    for idx, kp in enumerate(kpoints, start=1):
        xs = [idx] * len(kp["energies"])
        ys = [e - shift for e in kp["energies"]]
        colors = [color_for_occupation(o) for o in kp["occupations"]]
        ax.scatter(xs, ys, c=colors, s=14, edgecolors="none", zorder=3)

        if show_index:
            # agrupar band indices cuando estan superpuestos o separados por <= 0.1 eV
            # (agrupamiento por cadena: se ordena por energia y se van uniendo
            # puntos consecutivos cuya diferencia de energia sea <= 0.1 eV)
            order = sorted(range(1, len(ys) + 1), key=lambda b: ys[b - 1])
            groups = []
            current_group = [order[0]]
            current_y = ys[order[0] - 1]
            for band_idx in order[1:]:
                y_val = ys[band_idx - 1]
                if abs(y_val - current_y) <= 0.1:
                    current_group.append(band_idx)
                else:
                    groups.append(current_group)
                    current_group = [band_idx]
                current_y = y_val
            groups.append(current_group)

            for group in groups:
                group_sorted = sorted(group)
                y_mean = sum(ys[b - 1] for b in group_sorted) / len(group_sorted)
                # si hay mas de 8 valores, se parten en filas de 8 (una debajo de otra)
                chunks = [group_sorted[i:i + 7] for i in range(0, len(group_sorted), 7)]
                label = "\n".join(", ".join(str(b) for b in chunk) for chunk in chunks)
                ax.annotate(
                    label,
                    xy=(idx, y_mean),
                    xytext=(4, 0),
                    textcoords="offset points",
                    fontsize=8,
                    va="center",
                    ha="left",
                    zorder=4,
                )

    ax.set_xlabel("k-point index")
    if show_ylabel:
        ax.set_ylabel("Energy (eV)" if shift == 0 else f"Energy - {shift} (eV)")
    ax.set_title(title)
    ax.set_xticks(range(1, n_k + 1))
    #ax.grid(alpha=0.3, zorder=0)

    # leyenda manual (se construye aqui pero se dibuja una sola vez desde main())
    from matplotlib.lines import Line2D
    legend_elems = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="blue", markersize=7, label="occ > 0.9"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="green", markersize=7, label="0.1 <= occ <= 0.9"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="red", markersize=7, label="occ < 0.1"),
    ]

    # sombreado de banda de valencia (azul) / banda de conduccion (roja)
    # las posiciones se ajustan segun el mismo "res" aplicado a las energias:
    #   vb_line = VBM - res   (linea superior de la region azul)
    #   cb_line = CBM - res   (linea inferior de la region roja)
    vb_line = vbm - shift
    cb_line = cbm - shift

    ax.set_xlim(min(range(1, n_k + 1)) - 0.5, max(range(1, n_k + 1)) + 0.5)
    ax.set_ylim(vbm - 1.7945 - res, cbm + 1.7551 - res)

    ymin, ymax = ax.get_ylim()
    ax.axhspan(ymin, vb_line, color="blue", alpha=0.15, zorder=1)
    ax.axhspan(cb_line, ymax, color="red", alpha=0.15, zorder=1)
    ax.axhline(vb_line, color="blue", linewidth=0.8, linestyle="--", alpha=0.6)
    ax.axhline(cb_line, color="red", linewidth=0.8, linestyle="--", alpha=0.6)
    legend_elems.append(Line2D([0], [0], color="blue", lw=6, alpha=0.15, label=f"VB (y<={vb_line:.3f})"))
    legend_elems.append(Line2D([0], [0], color="red", lw=6, alpha=0.15, label=f"CB (y>={cb_line:.3f})"))

    return legend_elems


def main():
    # permite opcionalmente seguir pasando el archivo por linea de comandos,
    # pero si no se pasa nada usa los valores definidos arriba en CONFIGURACION MANUAL
    parser = argparse.ArgumentParser(description="Plot QE spin-polarized bands colored by occupation.")
    parser.add_argument("outfile", nargs="?", default=None, help="Archivo .out de Quantum ESPRESSO")
    parser.add_argument("-o", "--output", default=OUTPUT_FILE, help="Nombre del archivo PNG de salida")
    parser.add_argument("--index", action="store_true",
                         help="Imprime el band index (empezando en 1) al costado de cada punto")
    parser.add_argument("--res", action="store_true",
                         help="Reescala las energias respecto al VBM (RES = VBM). Sin este flag, RES = 0.0")
    args = parser.parse_args()

    vbm = VBM
    cbm = CBM
    res = VBM if args.res else 0.0

    # prioridad: argumento por linea de comandos > INPUT_FILE en config > autodeteccion
    if args.outfile is not None:
        infile = args.outfile
    elif INPUT_FILE is not None:
        infile = INPUT_FILE
    else:
        infile = find_out_file(".")
        print(f"Archivo .out detectado automaticamente: {infile}")

    with open(infile, "r", errors="ignore") as f:
        text = f.read()

    sections = split_spin_sections(text)
    up_kpoints = parse_section(sections["UP"])
    down_kpoints = parse_section(sections["DOWN"])

    fig, axes = plt.subplots(1, 2, figsize=(10, 8), sharey=True)
    plot_spin_channel(axes[0], up_kpoints, "SPIN UP", vbm=vbm, cbm=cbm, res=res,
                       show_index=args.index, show_ylabel=True)
    legend_elems = plot_spin_channel(axes[1], down_kpoints, "SPIN DOWN", vbm=vbm, cbm=cbm, res=res,
                                      show_index=args.index, show_ylabel=False)

    # leyenda unica, fuera del chart derecho, centrada verticalmente a su costado
    if legend_elems:
        fig.legend(
            handles=legend_elems,
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            bbox_transform=axes[1].transAxes,
            fontsize=8,
        )

    title = "Bandas de energia vs k-point (color = numero de ocupacion)"
    if res != 0:
        title += f"\nreescalado: E - {res} eV"
    #fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(args.output, dpi=150, bbox_inches="tight")
    print(f"Figura guardada en: {args.output}")
    print(f"SPIN UP: {len(up_kpoints)} k-points encontrados")
    print(f"SPIN DOWN: {len(down_kpoints)} k-points encontrados")


if __name__ == "__main__":
    main()
