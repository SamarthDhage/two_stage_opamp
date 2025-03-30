import os
import re
import csv
import time
import subprocess
import numpy as np

# Set LTspice Path
LTSPICE_PATH = r"C:\Program Files\ADI\LTspice\LTspice.exe"

# File Paths
NETLIST_FILE = r"D:\jupyter\Practice\VLSI_final\final_ops_schema copy.net"
MODIFIED_NETLIST_FILE = "final_modified.net"
LOG_FILE = "final_modified.log"
CSV_FILE = "two_stage_opamp_results.csv"

# Define random parameter sweep ranges
NUM_SAMPLES = 10  # Limit total simulations
def to_human_readable(value):
    """Convert value to human-readable format (with units)."""
    if value < 1e-9:
        return f"{value*1e12:.3f}p"  # picometers (p)
    elif value < 1e-6:
        return f"{value*1e9:.3f}n"  # nanometers (n)
    elif value < 1e-3:
        return f"{value*1e6:.3f}u"  # micrometers (u)
    elif value < 1:
        return f"{value*1e3:.3f}m"  # millimeters (m)
    else:
        return f"{value:.3f}"  # meters (m)

W1_values = np.random.uniform(2e-6, 24e-6, NUM_SAMPLES)
W3_values = np.random.uniform(3e-6, 28e-6, NUM_SAMPLES)
W5_values = np.random.uniform(2e-6, 24e-6, NUM_SAMPLES)
W6_values = np.random.uniform(32e-6, 360e-6, NUM_SAMPLES)
W7_values = np.random.uniform(14e-6, 150e-6, NUM_SAMPLES)

L1_values = np.random.uniform(180e-9, 520e-9, NUM_SAMPLES)
L3_values = np.random.uniform(180e-9, 520e-9, NUM_SAMPLES)
L5_values = np.random.uniform(180e-9, 520e-9, NUM_SAMPLES)
L6_values = np.random.uniform(180e-9, 520e-9, NUM_SAMPLES)
L7_values = np.random.uniform(180e-9, 520e-9, NUM_SAMPLES)

IB_values = np.random.uniform(10e-6, 30e-6, NUM_SAMPLES)
CC_values = np.random.uniform(0.44e-12, 2.99e-12, NUM_SAMPLES)


W1_values = list(map(to_human_readable, W1_values))
W3_values = list(map(to_human_readable, W3_values))
W5_values = list(map(to_human_readable, W5_values))
W6_values = list(map(to_human_readable, W6_values))
W7_values = list(map(to_human_readable, W7_values))

L1_values = list(map(to_human_readable, L1_values))
L3_values = list(map(to_human_readable, L3_values))
L5_values = list(map(to_human_readable, L5_values))
L6_values = list(map(to_human_readable, L6_values))
L7_values = list(map(to_human_readable, L7_values))

IB_values = list(map(to_human_readable, IB_values))
CC_values = list(map(to_human_readable, CC_values))

# Function to modify .net file
def modify_ltspice_netlist(W1, L1, W3, L3, W5, L5, W6, L6, W7, L7, IB, CC):
    with open(NETLIST_FILE, "r") as file:
        netlist_text = file.read()

    # Replace parameters
    replacements = {
        "{W1}": f"{W1}", "{L1}": f"{L1}",
        "{W3}": f"{W3}", "{L3}": f"{L3}",
        "{W5}": f"{W5}", "{L5}": f"{L5}",
        "{W6}": f"{W6}", "{L6}": f"{L6}",
        "{W7}": f"{W7}", "{L7}": f"{L7}",
        "{IB}": f"{IB}", "{CC}": f"{CC}"
    }

    for key, val in replacements.items():
        netlist_text = netlist_text.replace(key, val)


    with open(MODIFIED_NETLIST_FILE, "w") as file:
        file.write(netlist_text)

# Function to run LTspice
def run_ltspice():
    cmd = f'"{LTSPICE_PATH}" -b {MODIFIED_NETLIST_FILE}'
    subprocess.run(cmd, shell=True)
    time.sleep(0)
    start_time = time.time()
    while not os.path.exists(LOG_FILE):
        if time.time() - start_time > 10:
            print("Error: LTspice log file not found.")
            return False
        time.sleep(10)
    return True

# Function to extract results from LTspice log
def extract_ltspice_log():
    # Open the log file and read the last 3 lines
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as file:
        # Go to the end of the file and get the last 3 lines
        lines = file.readlines()[-3:]

    # Join the last 3 lines to get the full content
    log_data = ''.join(lines)

    # Extract Gain and Gain Phase
    gain_match = re.search(r"Gain:\sV\(vout\)=\(([-\d.e+]+)dB,\s*([-\d.e+]+)°\)", log_data)
    gain = float(gain_match.group(1)) if gain_match else None
    gain_phase = float(gain_match.group(2)) if gain_match else None

    # Extract UGBW
    ugbw_match = re.search(r"UGBW:\smag\(V\(vout\)\)=1\sAT\s([-\d.e+]+)", log_data)
    ugbw = float(ugbw_match.group(1)) if ugbw_match else None

    # Extract PM (Phase Margin)
    pm_match = re.search(r"PM:\sph\(V\(vout\)\)=\(([-\d.e+]+)dB,\s*([-\d.e+]+)°\)", log_data)
    pm_db = float(pm_match.group(1)) if pm_match else None
    pm_ph = float(pm_match.group(2)) if pm_match else None  # Phase margin in degrees

    return [gain, gain_phase, ugbw, pm_db, pm_ph]



# Create CSV and run parameter sweep
with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["W1", "L1", "W3", "L3", "W5", "L5", "W6", "L6", "W7", "L7", "IB", "CC", "Gain", "Gain_Phase", "UGBW", "PM_db", "PM_PH"])
    
    for i in range(NUM_SAMPLES):
        W1, L1 = W1_values[i], L1_values[i]
        W3, L3 = W3_values[i], L3_values[i]
        W5, L5 = W5_values[i], L5_values[i]
        W6, L6 = W6_values[i], L6_values[i]
        W7, L7 = W7_values[i], L7_values[i]
        IB, CC = IB_values[i], CC_values[i]
        
        print(f"Running simulation {i+1}/{NUM_SAMPLES}...")
        modify_ltspice_netlist(W1, L1, W3, L3, W5, L5, W6, L6, W7, L7, IB, CC)
        
        if run_ltspice():
            results = extract_ltspice_log()
            
            writer.writerow([W1, L1, W3, L3, W5, L5, W6, L6, W7, L7, IB, CC] + results)
        else:
            print("Skipping due to simulation error.")
