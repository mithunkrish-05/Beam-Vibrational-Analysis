"""
Beam Vibration Processor
Author: mithunkrish-05
Interactive script for filtering, analyzing, plotting and exporting
frequency & Young's Modulus results from CSV trial data.
"""

#Installing and Importing Libraries
import sys
import subprocess

def ensure(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing package: {pkg}…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for pkg in ("numpy", "pandas", "matplotlib", "scipy", "openpyxl"):
    ensure(pkg)
    
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import openpyxl
from pathlib import Path

#Read
def read_csv(file_path):
    df = pd.read_csv(file_path)
    time = df.iloc[:,1].values
    qlvl = df.iloc[:,0].values
    return time, qlvl
#Filter
def low_pass(data, cutoff=70, fs=5000, order=4):
    nyq = 0.5 * fs
    b,a = butter(order, cutoff/nyq, btype='low', analog=False)
    return filtfilt(b, a, data)
#Crop
def crop_signal(time, data, frac=0.1):
    amp = np.abs(data)
    thresh = frac * amp.max()
    idx = np.where(amp > thresh)[0]
    return time[idx[0]:idx[-1]+1], data[idx[0]:idx[-1]+1]
#Crossings
def find_crossings(time, data):
    xs = []
    for i in range(1,len(data)):
        if data[i-1]*data[i]<0:
            xs.append(time[i])
    return xs
#Frequency
def calc_frequency(n_cross, t_period):
    cycles = (n_cross-1)/2 if n_cross>1 else 0
    return cycles/t_period if t_period>0 else 0
#Young's Modulus
def calc_youngs_modulus(f, b, h, rho, I, L):
    q = rho*b*h
    E = ((f/0.56)**2 * q * L**4)/I
    return E/1e9  # GPa

def prompt(prompt_txt, default=None, cast=str):
    suf = f" [{default}]" if default is not None else ""
    while True:
        val = input(f"{prompt_txt}{suf}: ").strip()
        if not val and default is not None:
            return default
        try:
            return cast(val)
        except:
            print(" ↳ invalid input, try again")

#User Input
def main():
    # User settings
    inp_dir   = Path(prompt("Input folder containing CSVs", "data", Path))
    lengths   = prompt("Lengths to process (mm), comma-sep", "120,160,200", str)
    trials    = prompt("Number of trials per length", 3, int)
    cutoff    = prompt("Filter cutoff freq (Hz)", 70, float)
    fs        = prompt("Sampling rate (Hz)", 5000, float)
    order     = prompt("Filter order", 4, int)
    frac      = prompt("Crop fraction of max amp", 0.1, float)
    b         = prompt("Beam width b (m)", 0.0255, float)
    h         = prompt("Beam thickness h (m)", 0.0008, float)
    rho       = prompt("Material density (kg/m³)", 7700, float)

    # Output options
    graph_mode = prompt("Graph output mode: save, display, or both", "both", str).lower()
    save_excel = prompt("Save Excel analysis? (Y/n)", "Y", str).lower().startswith('y')
    if graph_mode not in ('save','display','both'):
        graph_mode = 'both'

    out_dir   = Path(prompt("Output folder for plots & Excel", "output", Path))
    out_dir.mkdir(parents=True, exist_ok=True)

    lengths = [int(x) for x in lengths.split(",")]
    I_moment = lambda b,h: (b*h**3)/12

    #Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Length(mm)", "Trial", "Frequency(Hz)", "Young's Modulus(GPa)"])

    all_E = []
    for L in lengths:
        this_length_E = []
        for t in range(1, trials+1):
            fname = inp_dir / f"{L}mm_Trial_{t}.csv"
            if not fname.exists():
                print(f" ⚠️  Missing file: {fname}")
                continue

            #Read & preprocess
            time, qlvl = read_csv(fname)
            centered    = qlvl - qlvl.mean()
            filt        = low_pass(centered, cutoff, fs, order)
            ctime, cdata = crop_signal(time, filt, frac)

            #Compute freq & E
            crossings = find_crossings(ctime, cdata)
            n_cross   = len(crossings)
            t_period  = crossings[-1]-crossings[0] if n_cross>1 else 0
            freq      = calc_frequency(n_cross, t_period)
            Evalue    = calc_youngs_modulus(freq, b, h, rho, I_moment(b,h), L/1000)
            this_length_E.append(Evalue)
            all_E.append(Evalue)

            #Plotting
            for label, series, color in [("filtered", filt, "blue"), ("cropped", cdata, "red")]:
                plt.figure(figsize=(8,4))
                data_x = time if label=='filtered' else ctime
                plt.plot(data_x, series, color=color, lw=0.8)
                plt.axhline(0, color='k', lw=0.5)
                plt.title(f"{L} mm Trial {t} – {label}")
                plt.xlabel("Time (s)")
                plt.ylabel("Quantisation level")
                plt.tight_layout()

                #Save
                if graph_mode in ('save','both'):
                    plot_fn = out_dir / f"{L}mm_Trial{t}_{label}.png"
                    plt.savefig(plot_fn, dpi=300)
                # Display
                if graph_mode in ('display','both'):
                    plt.show()
                plt.close()

            #Record results
            ws.append([L, t, round(freq,2), round(Evalue,2)])
            print(f"✔️  {L}mm Trial {t}: f={freq:.2f}Hz, E={Evalue:.2f}GPa")

        #Length average
        if this_length_E:
            avg_E = sum(this_length_E)/len(this_length_E)
            ws.append([L, "avg", "", round(avg_E,2)])

    #Overall average
    if all_E:
        overall = sum(all_E)/len(all_E)
        ws.append(["overall", "", "", round(overall,2)])

    #Save Excel
    if save_excel:
        excel_fn = out_dir / "beam_analysis.xlsx"
        wb.save(excel_fn)
        print(f"\n✅ Analysis complete. Excel → {excel_fn}")
    else:
        print("\nℹ️ Skipped saving Excel analysis.")

if __name__=="__main__":
    main()
