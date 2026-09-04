#!/usr/bin/env python3
# Written by Joseph P.Vera
# 2024-10

"""
Usage:
      python3 phonpllot.py [--x] [--y] [--tdos] [--pdos] [--ter] [--band] [--tband] [--split]

Plot DOS, PDOS, thermal properties and band structure from phonopy outputs.

Expected input files:
    Total DOS   -> total_dos.dat
    PDOS        -> projected_dos.dat  (+ pdos.conf for ATOM_NAME labels)
    Thermal     -> thermal.dat
    Band        -> band.dat            (+ band.conf for BAND_LABELS)
    Mixed bands -> band_nac.dat and band_nonac.dat  (+ band.conf)

Usage:
    phonplot.py --tdos                     # Total DOS
    phonplot.py --pdos                     # Partial DOS
    phonplot.py --ter                      # Thermal properties
    phonplot.py --band                     # Band structure
    phonplot.py --tband                    # Band structure with and without NAC
    phonplot.py --tdos --x 0 12 --y -1 23  # set axis ranges
    phonplot.py --split                    # each branch with different color
"""
import re
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def _apply_ranges(x_range, y_range):
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

def _finish(outfile):
    plt.legend()
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    #plt.show()
    plt.close()

def _read_conf_value(conf_file, key):
    """Grab the right-hand side of `KEY = ...` from a phonopy .conf file."""
    with open(conf_file) as f:
        for line in f:
            if key in line and '=' in line:
                return line.split('=', 1)[1].strip()
    return ''

def get_atomic_symbols(conf_file='pdos.conf'):
    value = _read_conf_value(conf_file, 'ATOM_NAME')
    return value.split() if value else []

def get_pdos_labels(conf_file='pdos.conf', data_file='projected_dos.dat'):
    """
    Build one label per PDOS column.
    - If len(symbols) == n_data_cols: use the symbols as-is (e.g. ATOM_NAME = B N).
    - Otherwise (equivalent atoms sharing a symbol, e.g. diamond): expand each
      symbol into Sym1, Sym2, ... across its equivalent columns.
    - If nothing lines up cleanly, fall back to col1, col2, ...
    """
    symbols = get_atomic_symbols(conf_file) or ['X']
    n_data_cols = pd.read_csv(data_file, sep=r'\s+', comment='#', header=None,
                               skiprows=1, nrows=1).shape[1] - 1

    if len(symbols) == n_data_cols:
        return symbols

    if len(symbols) < n_data_cols and n_data_cols % len(symbols) == 0:
        per_symbol = n_data_cols // len(symbols)
        if per_symbol == 1:
            return symbols
        return [f"{s}{i+1}" for s in symbols for i in range(per_symbol)]

    return [f"col{i+1}" for i in range(n_data_cols)]

def get_band_labels(config_file='band.conf'):
    label_string = _read_conf_value(config_file, 'BAND_LABELS').replace(r'\Gamma', r'$\Gamma$')
    parts = re.findall(r'\$\\Gamma\$|[A-Za-z]+(?::[A-Za-z]+)?', label_string)
    return [p.replace(':', '|') for p in parts]

def _load_band_file(path):
    """Return (k_path breakpoints, data array) for a phonopy band.dat-style file."""
    with open(path) as f:
        f.readline()
        k_path = list(map(float, f.readline().strip()[1:].split()))
    data = np.loadtxt(path, comments='#', skiprows=2)
    return k_path, data

BRANCH_COLORS = ['xkcd:red', 'xkcd:blue', 'xkcd:green', 'xkcd:orange', 'xkcd:purple',
                  'xkcd:magenta', 'xkcd:brown', 'xkcd:yellow', 'xkcd:crimson', 'xkcd:gold',
                  'xkcd:darkblue', 'xkcd:navy', 'xkcd:olive', 'xkcd:black', 'xkcd:indigo', 'xkcd:cyan']

def _band_blocks(data):
    """Split concatenated band.dat data into (start, end) index pairs, one per branch."""
    starts = np.where(np.concatenate(([True], np.diff(data[:, 0]) < 0)))[0]
    ends = list(starts[1:]) + [len(data)]
    return list(zip(starts, ends))

def _plot_band_blocks(data, ax, color, label):
    """Plot every branch in a single color, with one legend entry."""
    for i, (start, end) in enumerate(_band_blocks(data)):
        block = data[start:end]
        ax.plot(block[:, 0], block[:, 1], linestyle='-', markersize=1,
                 c=color, label=label if i == 0 else "")

def _plot_band_blocks_split(data, ax, colors=BRANCH_COLORS):
    """Plot each branch in its own color with its own 'Branch N' legend entry."""
    for i, (start, end) in enumerate(_band_blocks(data)):
        block = data[start:end]
        color = colors[i % len(colors)]
        ax.plot(block[:, 0], block[:, 1], linestyle='-', markersize=1,
                 c=color, label=f'Branch {i + 1}')
                 
# --------------------------------------------------------------------------- #
# Plot functions
# --------------------------------------------------------------------------- #
def plot_total_dos(file_path='total_dos.dat', x_range=None, y_range=None):
    x, y = np.loadtxt(file_path, comments='#', skiprows=1, unpack=True, usecols=(0, 1))

    plt.plot(x, y, label="Total DOS", color='r')
    plt.fill_between(x, y, alpha=0.1, color='r')
    plt.xlabel('Frequency (THz)', fontsize=14)
    plt.ylabel('DOS (States/THz)', fontsize=14)
    _apply_ranges(x_range, y_range)
    _finish('tdos.png')

def plot_pdos(file_path='projected_dos.dat', conf_file='pdos.conf', x_range=None, y_range=None):
    data = np.loadtxt(file_path, comments='#', skiprows=1)
    x, y_columns = data[:, 0], data[:, 1:].T

    labels = get_pdos_labels(conf_file, file_path)
    labels += [f"col{i+1}" for i in range(len(labels), len(y_columns))]

    colors = cm.tab10.colors
    for i, y in enumerate(y_columns):
        color = colors[i % len(colors)]
        plt.plot(x, y, label=labels[i], color=color)
        plt.fill_between(x, y, alpha=0.1, color=color)

    plt.xlabel('Frequency (THz)', fontsize=14)
    plt.ylabel('PDOS (States/THz)', fontsize=14)
    _apply_ranges(x_range, y_range)
    _finish('pdos.png')

def plot_thermal(file_path='thermal.dat', x_range=None, y_range=None):
    labels = ['Helmholtz Free energy (kJ/mol)', 'Entropy (J/K.mol)',
              'Heat Capacity $C_{v}$ (J/K.mol)', 'Energy (kJ/mol)']
    colors = ['g', 'orange', 'b', 'r']

    with open(file_path) as f:
        rows = [ln.split() for ln in f
                if ln.split() and all(p.replace('.', '', 1).lstrip('-').isdigit() for p in ln.split())]
    data = pd.DataFrame(rows, dtype=float)

    x = data[0]
    for i, (col, label, color) in enumerate(zip([1, 2, 3, 4], labels, colors)):
        plt.plot(x, data[col], label=label, color=color)

    plt.xlim(x.min(), x.max())
    plt.xlabel('Temperatura (K)', fontsize=14)
    _apply_ranges(x_range, y_range)
    _finish('thermal_properties.png')

def _plot_band(bands, config_file='band.conf', x_range=None, y_range=None,
               figsize=None, label_fontsize=None, linewidth=0.9, outfile='band.png',
               split=False):
    """
    bands: list of (file_path, color, legend_label) to overlay on one axis.
    split: if True, plot every branch of each file in its own color
           (only sensible with a single entry in `bands`).
    """
    k_path, _ = _load_band_file(bands[0][0])
    fig, ax = plt.subplots()

    for path, color, label in bands:
        _, data = _load_band_file(path)
        if split:
            _plot_band_blocks_split(data, ax)
        else:
            _plot_band_blocks(data, ax, color, label)

    for x in k_path[1:-1]:
        ax.axvline(x=x, color='k', linestyle='-', linewidth=linewidth)

    ax.set_ylabel('Frequency (THz)', fontsize=label_fontsize or 14)
    if figsize:
        fig.set_size_inches(*figsize)
    plt.xlim(0.0, k_path[-1])
    plt.axhline(y=0.00, color='k', linestyle='dashed')

    ax.set_xticks(k_path)
    ax.set_xticklabels(get_band_labels(config_file), fontsize=label_fontsize)

    _apply_ranges(x_range, y_range)
    
    if split:
        plt.legend(loc='lower right')
        
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    #plt.show()
    plt.close()

def plot_single_band(nac_file='band.dat', color_nac='r', x_range=None, y_range=None, split=False):
    _plot_band([(nac_file, color_nac, None)], # 'Without NAC'
               x_range=x_range, y_range=y_range, outfile= 'band-split.png' if split else 'band.png', split=split)

def plot_mix_band(nac_file='band_nac.dat', no_nac_file='band_nonac.dat',
                   color_nac='xkcd:red', color_no_nac='xkcd:blue', x_range=None, y_range=None):
    _plot_band([(nac_file, color_nac, 'With NAC'), (no_nac_file, color_no_nac, 'Without NAC')],
               x_range=x_range, y_range=y_range, figsize=(12, 8),
               label_fontsize=14, linewidth=0.2, outfile='band_combinate.png')

def main():
    parser = argparse.ArgumentParser(description='Plotting functions for phonon data.')
    parser.add_argument('--tdos', action='store_true', help='Plot total DOS.')
    parser.add_argument('--pdos', action='store_true', help='Plot projected DOS.')
    parser.add_argument('--ter', action='store_true', help='Plot thermal properties.')
    parser.add_argument('--band', action='store_true', help='Plot single band structure.')
    parser.add_argument('--tband', action='store_true', help='Plot mixed band structure (NAC vs no NAC).')
    parser.add_argument('--split', action='store_true',
                         help='With --band, color each branch separately (Branch 1, 2, ...).')
    parser.add_argument('--x', nargs=2, type=float, metavar=('MIN', 'MAX'), help='Set x-axis range.')
    parser.add_argument('--y', nargs=2, type=float, metavar=('MIN', 'MAX'), help='Set y-axis range.')
    args = parser.parse_args()

    x_range = tuple(args.x) if args.x else None
    y_range = tuple(args.y) if args.y else None

    dispatch = {
        'tdos': plot_total_dos,
        'pdos': plot_pdos,
        'ter': plot_thermal,
        'band': plot_single_band,
        'tband': plot_mix_band,
    }

    for flag, func in dispatch.items():
        if getattr(args, flag):
            kwargs = dict(x_range=x_range, y_range=y_range)
            if flag == 'band':
                kwargs['split'] = args.split
            func(**kwargs)
            return

    print("No valid argument provided. Please specify one of the following options:")
    print("--tdos, --pdos, --ter, --band, --tband")

if __name__ == '__main__':
    main()
