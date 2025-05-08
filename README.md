# Beam-Vibrational-Analysis

Interactive Python script for filtering, analyzing, plotting, and exporting vibration data of a ruler (modeled as a beam) from CSV trial measurements.

---

## Data Acquisition

Follow these steps to record and prepare your vibration data CSVs:

1. **Beam/Ruler Setup**

   * Secure the ruler or beam (cantilever at one end or supported at both ends).
   * Attach a suitable sensor (accelerometer, displacement transducer) near the free end or at a consistent point.

2. **Hardware & Sampling**

   * Use a microcontroller or DAQ (Arduino, Raspberry Pi + ADC, NI-DAQ, etc.).
   * Sample at a constant rate (e.g. 5000 Hz).
   * Log two columns (no header) in CSV format:

     1. **Quantisation level** (raw sensor reading)
     2. **Time (s)** (timestamp or sample index ÷ sampling rate)

3. **Conduct Trials**

   * For each beam length (e.g. 120 mm, 160 mm, 200 mm), excite the beam (pluck or impact).
   * Record a few seconds until oscillation decays.
   * Save each trial as `LENGTHmm_Trial_N.csv`, for example:

     ```text
     120mm_Trial_1.csv
     120mm_Trial_2.csv
     160mm_Trial_1.csv
     ```

4. **Organize Files**

   * Place all CSVs in one folder (default: `data/`).

---

## Features

* **Auto‑installs** dependencies: `numpy`, `pandas`, `matplotlib`, `scipy`, `openpyxl`.
* **Interactive prompts** for directories, lengths, filter settings, material parameters, and output options.
* **Multi‑trial support** across various beam lengths.
* **Signal processing**: centering, Butterworth low‑pass, cropping, zero‑crossing detection.
* **Calculations**: frequency per trial, Young’s Modulus per trial, per‑length & overall averages.
* **Graph outputs**: save, display, or both.
* **Excel summary**: optional output of `ruler_analysis.xlsx`.

---

## Requirements

* Python 3.7+
* OS: Windows, macOS, or Linux
* Terminal or IDE console

---

## Installation

```bash
git clone https://github.com/mithunkrish-05/Beam-Vibrational-Analysis.git
cd Beam-Vibrational-Analysis
```

*Optional venv:*

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.\.venv\Scripts\activate     # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

*The script also auto‑installs missing packages if run without a venv.*

---

## Usage

```bash
python Vibrational_Analysis.py
```

You will be prompted for:

1. **Input folder** containing your CSVs (default `data/`).
2. **Lengths** in mm to process (comma‑separated, e.g. `120,160,200`).
3. **Trials** per length (e.g. `3`).
4. **Filter cutoff freq** in Hz (e.g. `70`).
5. **Sampling rate** in Hz (e.g. `5000`).
6. **Filter order** (e.g. `4`).
7. **Crop fraction** of peak amplitude (e.g. `0.1`).
8. **Beam width b** in meters (e.g. `0.0255`).
9. **Beam thickness h** in meters (e.g. `0.0008`).
10. **Material density** in kg/m³ (e.g. `7700`).
11. **Graph mode**: `save`, `display`, or `both`.
12. **Save Excel analysis?** Y/n.
13. **Output folder** for plots & Excel (default `output/`).

The script will:

* Process each trial, apply filter & crop, compute zero‑crossing frequency & Young’s Modulus.
* **Save** and/or **display** filtered & cropped plots.
* Print results to terminal.
* Optionally generate `beam_analysis.xlsx` in your output folder.

---

## Example Session

```
$ python ruler_analysis.py
Input folder containing CSVs [data]: data
Lengths to process (mm), comma-sep [120,160,200]: 120,160
Number of trials per length [3]: 3
Filter cutoff freq (Hz) [70]: 80
Sampling rate (Hz) [5000]:
Filter order [4]:
Crop fraction of max amp [0.1]: 0.12
Beam width b (m) [0.0255]:
Beam thickness h (m) [0.0008]:
Material density (kg/m³) [7700]:
Graph mode: save, display, or both [both]: save
Save Excel analysis? [Y]:
Output folder for plots & Excel [output]: results
✔️  120mm Trial 1: f=12.34 Hz, E=5.67 GPa
✔️  120mm Trial 2: f=11.98 Hz, E=5.49 GPa
…
✅ Analysis complete. Excel → results/ruler_analysis.xlsx

