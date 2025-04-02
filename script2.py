import pandas as pd
import re
import os
import subprocess

# File paths
csv_file = "parameters.csv"         # CSV containing W, L, IB, CC values
netlist_template = r"D:\jupyter\Practice\VLSI_final\final_ops_schema copy 2.net"  # Template netlist with placeholders
netlist_file = "final_modified.net"     # Modified netlist file
log_file = "final_modified.log"          # LTspice output log

# Read CSV file
df = pd.read_csv(csv_file)

# Iterate over each row in CSV
for index, row in df.iterrows():
    W1, L1, W3, L3, W5, L5, W6, L6, W7, L7, IB, CC = row

    # Create replacements dictionary
    replacements = {
        "{W1}": f"{W1}", "{L1}": f"{L1}",
        "{W3}": f"{W3}", "{L3}": f"{L3}",
        "{W5}": f"{W5}", "{L5}": f"{L5}",
        "{W6}": f"{W6}", "{L6}": f"{L6}",
        "{W7}": f"{W7}", "{L7}": f"{L7}",
        "{IB}": f"{IB}", "{CC}": f"{CC}"
    }

    # Modify netlist file
    with open(netlist_template, "r") as file:
        netlist_content = file.read()

    for key, value in replacements.items():
        netlist_content = netlist_content.replace(key, value)
    

    with open(netlist_file, "w") as file:
        file.write(netlist_content)

    # Run LTspice
    ltspice_exe = r"C:\Program Files\ADI\LTspice\LTspice.exe"
    subprocess.run([ltspice_exe, "-b", netlist_file], check=True)

    # Extract results from log file
    with open(log_file, "r") as file:
        log_content = file.read()
        

    # Regex patterns for measurements
    power_match = re.search(r"Total_Power:\s*P_M\d+\s*\+\s*.*=\s*([-\d.eE+]+)", log_content)
    total_power = float(power_match.group(1)) if power_match else None

    # Extract Slew Rate
    sr_match = re.search(r"SR_calc:\s*IB/CC\s*=\s*([-\d.eE+]+)", log_content)
    slew_rate = float(sr_match.group(1)) if sr_match else None

    # Extract Total Area
    area_match = re.search(r"TOTAL_AREA:\s*AREA_W\d+\s*\+\s*.*=\s*([-\d.eE+]+)", log_content)
    total_area = float(area_match.group(1)) if area_match else None

# Print results

    print(f"Run {index + 1}: TOTAL_AREA = {total_area}, SR_calc = {slew_rate}, Total_Power = {total_power}")

    # Save results
    if index == 0:
        with open("results.csv", "w") as results_file:
            results_file.write("W1,L1,W3,L3,W5,L5,W6,L6,W7,L7,IB,CC,total_area,slew_rate,total_power\n")
    with open("results.csv", "a") as results_file:
        results_file.write(f"{W1},{L1},{W3},{L3},{W5},{L5},{W6},{L6},{W7},{L7},{IB},{CC},{total_area},{slew_rate},{total_power}\n")

print("Simulation complete. Results saved to results.csv")
