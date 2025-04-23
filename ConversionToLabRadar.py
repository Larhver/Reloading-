import pandas as pd
import argparse
import os
from datetime import date


def convert_garmin_to_labradar(garmin_csv,makeDir=True):
    labradar_csv = os.path.splitext(garmin_csv)[0] + "_labradar.csv"

    # Load Garmin CSV file, skipping metadata rows
    df = pd.read_csv(garmin_csv, skiprows=1)

    # Ensure Garmin CSV has expected columns
    expected_columns = ['#', 'SPEED (MPS)', 'TIME']
    df = df.dropna().reset_index(drop=True)  # Remove empty rows
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("Unexpected Garmin CSV format. Ensure it has '#', 'SPEED (MPS)', and 'TIME' columns.")

    # Clean and convert SPEED (MPS) column
    df['SPEED (MPS)'] = df['SPEED (MPS)'].astype(str).str.strip().str.replace(',', '.').astype(float)

    # Create LabRadar format
    labradar_header = [
        "sep=;",
        "Device ID;LBR-0018237;;",
        "",
        "Series No;0001;;",
        f"Total number of shots;{len(df)};;",
        "",
        "Units velocity;m/s;;",
        "Units distances;m;;",
        "Units kinetic energy;ft-lbf;;",
        "Units weight;grain (gr);;",
        "",
        f"Stats - Average;{df['SPEED (MPS)'].mean():.2f};m/s;",
        f"Stats - Highest;{df['SPEED (MPS)'].max():.2f};m/s;",
        f"Stats - Lowest;{df['SPEED (MPS)'].min():.2f};m/s;",
        f"Stats - Ext. Spread;{df['SPEED (MPS)'].max() - df['SPEED (MPS)'].min():.2f};m/s;",
        f"Stats - Std. Dev;{df['SPEED (MPS)'].std():.2f};m/s;",
        "",
        "Shot ID;V0;Date;Time"
    ]

    labradar_data = df.copy()
    labradar_data['Shot ID'] = labradar_data['#'].astype(str).str.zfill(4)
    labradar_data['V0'] = labradar_data['SPEED (MPS)'].round(2)
    labradar_data['Date'] = pd.Timestamp.now().strftime('%m-%d-%Y')
    labradar_data['Time'] = df['TIME']

    # Save as LabRadar CSV format
    if makeDir == True:
        ndirname = date.today().strftime("%y.%m.%d")
        if os.path.isdir(date.today().strftime("%y.%m.%d")):
            pass
        else:
            os.makedirs(os.path.join(os.getcwd(),ndirname))
    else:
        ndirname=""
    pathOut = os.path.join(os.getcwd(),ndirname,labradar_csv)
    print(pathOut)
    with open(pathOut, 'w') as f:
        for line in labradar_header:
            f.write(line + "\n")

    labradar_data[['Shot ID', 'V0', 'Date', 'Time']].to_csv(pathOut, mode='a', index=False, sep=';', header=False)
    print(f"Converted Garmin CSV to LabRadar format and saved as {labradar_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Garmin CSV to LabRadar CSV format.")
    parser.add_argument("input_file", help="Path to the Garmin CSV file.")
    args = parser.parse_args()

    convert_garmin_to_labradar(args.input_file)
