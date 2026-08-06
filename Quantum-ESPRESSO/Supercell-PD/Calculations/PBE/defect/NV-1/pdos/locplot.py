#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2026-08

#!/usr/bin/env python3
"""
plot_bands_localization.py
---------------------------
Lee un archivo tipo "localization.dat" (salida post-procesada de projwfc.x,
ya resumida por banda/atomo con columnas s, p_x, p_y, p_z, tot), extrae los
bloques SPIN UP / SPIN DOWN, y para cada k-point extrae, por banda:
    - energia (eV)
    - grado de localizacion = suma de la columna "tot" de TODOS los atomos
      listados en esa banda (el archivo ya trae, para cada banda/k-point,
      solo el subconjunto de atomos relevante -- esa lista de atomos varia
      banda a banda y k-point a k-point, por lo que no se fija de antemano;
      simplemente se suman todas las filas de atomo presentes en el bloque,
      ignorando el encabezado y la fila de resumen "tot")

Regla de graficado (scatter, x = indice de k-point, y = energia eV):
    El color de cada punto ya NO es discreto (rojo/verde/azul por ocupacion,
    como en plot_bands_spin.py) sino continuo: se usa un colormap + colorbar
    para representar el grado de localizacion calculado arriba.

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

        python plot_bands_localization.py

    Si dejas INPUT_FILE = None, el script busca automaticamente un archivo
    .dat en la carpeta actual, ignorando los logs tipo slurm-1234.out.

    Usa --index para imprimir el band index (empezando en 1) al costado de
    cada punto graficado (si varios estan superpuestos o separados por
    <= 0.1 eV, se agrupan en una lista, ej. "12, 13, 14, 15"):

        python plot_bands_localization.py --index

    Usa --res para reescalar las energias respecto al VBM (RES = VBM). Sin
    este flag, RES = 0.0 (no se reescala):

        python plot_bands_localization.py --res

    Usa --tot para que el grado de localizacion de cada banda sea el valor
    de la fila de resumen "tot" que ya trae el archivo (ultima columna),
    en vez de la suma manual de las filas de atomo individuales:

        python plot_bands_localization.py --tot
"""

import os
import re
import glob
import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl


# =====================================================================
# CONFIGURACION MANUAL - edita estos valores segun tu caso
# =====================================================================
INPUT_FILE = None                     # ruta a tu archivo .dat, o None para
                                       # buscar automaticamente en la carpeta
                                       # actual (ignorando slurm-*.out)
OUTPUT_FILE = "eigenplot_localization.png"  # nombre del PNG de salida

VBM = 12.82469624   # valor del VBM (eV) -- SIEMPRE se debe definir
CBM = 18.08184593   # valor del CBM (eV) -- SIEMPRE se debe definir

CMAP = "viridis"     # colormap usado para el grado de localizacion
# =====================================================================


FLOAT_RE = re.compile(r"[-+]?\d+\.\d+")

SPIN_UP_RE = re.compile(r"=+\s*\n\s*SPIN\s+UP\s*\n\s*=+", re.IGNORECASE)
SPIN_DOWN_RE = re.compile(r"=+\s*\n\s*SPIN\s+DOWN\s*\n\s*=+", re.IGNORECASE)

KPOINT_HEADER_RE = re.compile(
    r"---\s*k-point\s+(\d+)\s*\(\s*k\s*=\s*([-+0-9.\s]+?)\)\s*---",
    re.IGNORECASE,
)

BAND_HEADER_RE = re.compile(
    r"Band\s+(\d+)\s+energy\s*=\s*([-+]?\d+\.\d+)\s*eV",
    re.IGNORECASE,
)


def find_dat_file(folder="."):
    """
    Busca automaticamente un archivo .dat en 'folder', ignorando los archivos
    de log de slurm tipo slurm-1234.out (chequeado solo por el nombre).
    """
    all_dat_files = glob.glob(os.path.join(folder, "*.dat"))
    dat_files = [f for f in all_dat_files if not re.match(r"^slurm-\d+\.out$", os.path.basename(f))]

    if not dat_files:
        raise FileNotFoundError(
            "No se encontro ningun archivo .dat valido en la carpeta "
            "(se ignoran los archivos tipo slurm-*.out)."
        )
    if len(dat_files) > 1:
        print(f"Aviso: se encontraron varios archivos .dat {sorted(dat_files)}, usando: {dat_files[0]}")

    return dat_files[0]


def split_spin_sections(text):
    """
    Divide el archivo en la seccion SPIN UP y SPIN DOWN.
    Si no existen esos marcadores (calculo no polarizado), devuelve
    todo el contenido como una unica seccion 'UP'.
    """
    up_marker = SPIN_UP_RE.search(text)
    down_marker = SPIN_DOWN_RE.search(text)

    if up_marker and down_marker:
        up_text = text[up_marker.end():down_marker.start()]
        down_text = text[down_marker.end():]
        return {"UP": up_text, "DOWN": down_text}
    else:
        return {"UP": text, "DOWN": ""}


def parse_atom_table(block_text, use_summary_row=False):
    """
    Dado el texto de una banda (tabla atom / s / p_x / p_y / p_z / tot):

    - use_summary_row=False (default): suma la columna 'tot' de TODAS las
      filas de atomo presentes en el bloque (el conjunto de atomos listado
      varia banda a banda / k-point a k-point, por eso no se filtra por una
      lista fija). Ignora la fila de encabezado ("atom  s  p_x ...") y la
      fila de resumen ("tot   ..."), que no representa un atomo individual.

    - use_summary_row=True: en vez de sumar las filas de atomo, se usa
      directamente el valor de la columna 'tot' de la fila de resumen
      ("tot   ...   0.997000"), que ya viene calculado en el archivo.
    """
    total = 0.0
    summary_value = 0.0
    for line in block_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith("atom"):
            continue
        parts = stripped.split()
        if parts[0].lower() == "tot":
            # fila de resumen: "tot   s_sum  px_sum  py_sum  pz_sum  tot_sum"
            floats = extract_floats_from_parts(parts[1:])
            if floats:
                summary_value = floats[-1]
            continue
        try:
            int(parts[0])  # confirma que la fila corresponde a un atomo
        except ValueError:
            continue
        floats = extract_floats_from_parts(parts[1:])
        if floats:
            total += floats[-1]  # ultima columna = "tot" de esa fila

    return summary_value if use_summary_row else total


def extract_floats_from_parts(parts):
    vals = []
    for p in parts:
        m = FLOAT_RE.fullmatch(p)
        if m:
            vals.append(float(p))
    return vals


def parse_section(section_text, use_summary_row=False):
    """
    Parsea una seccion (UP o DOWN) y devuelve una lista de k-points, cada
    uno con sus energias y grados de localizacion:
        [ {"k": (kx,ky,kz), "energies": [...], "localization": [...]}, ... ]
    """
    kpoints = []

    kp_headers = list(KPOINT_HEADER_RE.finditer(section_text))
    if not kp_headers:
        return kpoints

    for i, kh in enumerate(kp_headers):
        kvec_str = kh.group(2).split()
        try:
            kvec = tuple(float(v) for v in kvec_str[:3])
        except ValueError:
            kvec = (None, None, None)

        kp_start = kh.end()
        kp_end = kp_headers[i + 1].start() if i + 1 < len(kp_headers) else len(section_text)
        kp_text = section_text[kp_start:kp_end]

        band_headers = list(BAND_HEADER_RE.finditer(kp_text))
        energies = []
        localization = []

        for j, bh in enumerate(band_headers):
            energy = float(bh.group(2))
            b_start = bh.end()
            b_end = band_headers[j + 1].start() if j + 1 < len(band_headers) else len(kp_text)
            band_block = kp_text[b_start:b_end]

            loc = parse_atom_table(band_block, use_summary_row)

            energies.append(energy)
            localization.append(loc)

        if energies:
            kpoints.append({"k": kvec, "energies": energies, "localization": localization})

    return kpoints


def plot_spin_channel(ax, kpoints, title, vbm, cbm, norm, cmap, res=0,
                       show_index=False, show_ylabel=True):
    if not kpoints:
        ax.set_title(f"{title} (sin datos)")
        return None

    shift = res
    n_k = len(kpoints)
    scatter_obj = None

    for idx, kp in enumerate(kpoints, start=1):
        xs = [idx] * len(kp["energies"])
        ys = [e - shift for e in kp["energies"]]
        cs = kp["localization"]
        scatter_obj = ax.scatter(xs, ys, c=cs, cmap=cmap, norm=norm, s=50,
                                  edgecolors="none", zorder=3)

        if show_index:
            # agrupar band indices cuando estan superpuestos o separados por
            # <= 0.1 eV (agrupamiento por cadena: se ordena por energia y se
            # van uniendo puntos consecutivos cuya diferencia sea <= 0.1 eV)
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
    ax.set_xticklabels([r'$\Gamma$'] + [str(i) for i in range(2, n_k + 1)])

    # sombreado de banda de valencia (azul) / banda de conduccion (roja)
    vb_line = vbm - shift
    cb_line = cbm - shift

    ax.set_xlim(min(range(1, n_k + 1)) - 0.5, max(range(1, n_k + 1)) + 0.5)
    ax.set_ylim(vbm - 1.7945 - res, cbm + 1.7551 - res)

    ymin, ymax = ax.get_ylim()
    ax.axhspan(ymin, vb_line, color="blue", alpha=0.15, zorder=1)
    ax.axhspan(cb_line, ymax, color="red", alpha=0.15, zorder=1)
    ax.axhline(vb_line, color="blue", linewidth=0.8, linestyle="--", alpha=0.6)
    ax.axhline(cb_line, color="red", linewidth=0.8, linestyle="--", alpha=0.6)

    return scatter_obj


def main():
    parser = argparse.ArgumentParser(
        description="Plot bands colored by atomic localization degree (from localization.dat)."
    )
    parser.add_argument("datfile", nargs="?", default=None, help="Archivo localization.dat")
    parser.add_argument("-o", "--output", default=OUTPUT_FILE, help="Nombre del archivo PNG de salida")
    parser.add_argument("--index", action="store_true",
                         help="Imprime el band index (empezando en 1) al costado de cada punto")
    parser.add_argument("--res", action="store_true",
                         help="Reescala las energias respecto al VBM (RES = VBM). Sin este flag, RES = 0.0")
    parser.add_argument("--tot", action="store_true",
                         help="Usa el valor de la fila de resumen 'tot' de cada banda (ya calculado en "
                              "el archivo) en vez de sumar las filas de atomo individuales.")
    args = parser.parse_args()

    vbm = VBM
    cbm = CBM
    res = VBM if args.res else 0.0

    if args.datfile is not None:
        infile = args.datfile
    elif INPUT_FILE is not None:
        infile = INPUT_FILE
    else:
        infile = find_dat_file(".")
        print(f"Archivo .dat detectado automaticamente: {infile}")

    with open(infile, "r", errors="ignore") as f:
        text = f.read()

    sections = split_spin_sections(text)
    up_kpoints = parse_section(sections["UP"], use_summary_row=args.tot)
    down_kpoints = parse_section(sections["DOWN"], use_summary_row=args.tot)

    # escala de color compartida entre ambos canales de spin, calculada
    # sobre el conjunto global de valores de localizacion
    all_vals = []
    for kp in up_kpoints + down_kpoints:
        all_vals.extend(kp["localization"])
    vmin = min(all_vals) if all_vals else 0.0
    vmax = max(all_vals) if all_vals else 1.0
    if vmin == vmax:
        vmax = vmin + 1e-9
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(CMAP)

    fig, axes = plt.subplots(1, 2, figsize=(11, 8), sharey=True, constrained_layout=True)
    plot_spin_channel(axes[0], up_kpoints, "SPIN UP", vbm=vbm, cbm=cbm, norm=norm, cmap=cmap,
                       res=res, show_index=args.index, show_ylabel=True)
    scatter_obj = plot_spin_channel(axes[1], down_kpoints, "SPIN DOWN", vbm=vbm, cbm=cbm, norm=norm, cmap=cmap,
                                     res=res, show_index=args.index, show_ylabel=False)

    if scatter_obj is None:
        # fallback: si SPIN DOWN no tiene datos, usar el scatter de SPIN UP para la colorbar
        for coll in axes[0].collections:
            scatter_obj = coll
            break

    if scatter_obj is not None:
        cbar = fig.colorbar(scatter_obj, ax=axes, location="right", pad=0.02, fraction=0.05)
        if args.tot:
            cbar.set_label("Grado de localizacion (valor 'tot' de la fila de resumen)")
        else:
            cbar.set_label("Grado de localizacion (suma de 'tot' de los atomos listados)")

    title = "Bandas de energia vs k-point (color = grado de localizacion atomica)"
    if res != 0:
        title += f"\nreescalado: E - {res} eV"
    fig.savefig(args.output, dpi=150)
    print(f"Figura guardada en: {args.output}")
    print(f"SPIN UP: {len(up_kpoints)} k-points encontrados")
    print(f"SPIN DOWN: {len(down_kpoints)} k-points encontrados")
    print(f"Rango de localizacion: [{vmin:.6f}, {vmax:.6f}]")


if __name__ == "__main__":
    main()
