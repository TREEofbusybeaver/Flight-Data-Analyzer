# =============================================================================
# FINAL ALL-IN-ONE FLIGHT DATA RECORDER ANALYZER (VERSION 3 - FINAL)
# This script automatically downloads data, analyzes it, and creates a plot.
# CORRECTION 2: Removed the buggy line that crashed the phase identification.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os


# --- Part 1: Automated Data Sourcing ---

def fetch_flight_data_and_save_as_csv(output_filepath):
    print(">>> STEP 0: Data file not found. Let's download some real flight data!")
    print(">>> This might take a minute...")

    try:
        from traffic.data.opensky import OpenSky
        opensky_client = OpenSky()
        print(">>> 'traffic' library is ready.")

        flight = opensky_client.history(
            "2019-08-01 07:00",  # Start time in UTC
            stop="2019-08-01 08:30",  # End time in UTC
            callsign="AFR6114"  # The flight's callsign
        )

        if flight is None or flight.data.empty:
            print("\n[ERROR] Could not fetch flight data.")
            return False

        df = flight.data[['timestamp', 'baroaltitude', 'velocity', 'vertrate']]
        df['time'] = df['timestamp'].apply(lambda t: t.timestamp())
        df.to_csv(output_filepath, index=False)

        print(f"\n>>> Data successfully downloaded and saved as '{output_filepath}'")
        time.sleep(2)
        return True

    except Exception as e:
        print(f"\n[ERROR] An error occurred during data fetching: {e}")
        return False


# --- Part 2: The Flight Data Analyzer ---

GROUND_ALTITUDE_THRESHOLD_FT = 150
CLIMB_VS_THRESHOLD_FPM = 500
CRUISE_ALTITUDE_THRESHOLD_FT = 30000
DESCENT_VS_THRESHOLD_FPM = -500


def load_and_prepare_data(filepath):
    print("\n>>> STEP 1: Loading and preparing data for analysis...")
    if not os.path.exists(filepath):
        if not fetch_flight_data_and_save_as_csv(filepath):
            return None

    df = pd.read_csv(filepath)
    df = df.rename(columns={'time': 'time_seconds'})
    df['altitude_ft'] = df['baroaltitude'] * 3.28084
    df['airspeed_kts'] = df['velocity'] * 1.94384
    df['vertical_speed_fpm'] = df['vertrate'] * 196.85
    df = df[['time_seconds', 'altitude_ft', 'airspeed_kts', 'vertical_speed_fpm']]
    df.dropna(inplace=True)
    df['time_seconds'] = df['time_seconds'] - df['time_seconds'].iloc[0]
    df = df.sort_values(by='time_seconds').reset_index(drop=True)
    print(f">>> Data ready. Found {len(df)} data points.")
    return df


def apply_phase_identification(df):
    print("\n>>> STEP 2: Identifying flight phases (Climb, Cruise, etc.)...")

    def identify_phase(row):
        alt, vs = row['altitude_ft'], row['vertical_speed_fpm']
        if alt < (df['altitude_ft'].min() + GROUND_ALTITUDE_THRESHOLD_FT): return 'On Ground / Taxi'
        if vs > CLIMB_VS_THRESHOLD_FPM: return 'Climb'
        if vs < DESCENT_VS_THRESHOLD_FPM: return 'Descent'
        if alt > CRUISE_ALTITUDE_THRESHOLD_FT: return 'Cruise'
        return 'Level Flight'

    df['phase'] = df.apply(identify_phase, axis=1)

    # --- THIS BUGGY LINE HAS BEEN REMOVED ---

    print(">>> Phase identification complete.")
    return df


def visualize_flight_data(df):
    print("\n>>> STEP 3: Generating the final plot...")
    sns.set_theme(style="whitegrid")
    phases = sorted(df['phase'].unique())  # Sort phases for consistent colors
    colors = sns.color_palette('viridis', n_colors=len(phases))
    phase_color_map = dict(zip(phases, colors))

    fig, ax1 = plt.subplots(figsize=(18, 8))
    ax1.plot(df['time_seconds'], df['altitude_ft'], color='black', label='Altitude (ft)', linewidth=2.5)
    ax1.set_xlabel('Time (seconds)', fontsize=12)
    ax1.set_ylabel('Altitude (ft)', fontsize=12)

    ax2 = ax1.twinx()
    ax2.plot(df['time_seconds'], df['airspeed_kts'], color='royalblue', label='Airspeed (kts)', linestyle='--',
             linewidth=2)
    ax2.set_ylabel('Airspeed (kts)', color='royalblue', fontsize=12)

    for i in range(len(df) - 1):
        ax1.axvspan(df['time_seconds'][i], df['time_seconds'][i + 1],
                    facecolor=phase_color_map.get(df['phase'][i], 'white'), alpha=0.3)

    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='black', lw=2.5, label='Altitude')]
    legend_elements.append(Line2D([0], [0], color='royalblue', lw=2, linestyle='--', label='Airspeed'))
    for phase in phases:
        legend_elements.append(
            plt.Rectangle((0, 0), 1, 1, fc=phase_color_map[phase], alpha=0.5, label=f'Phase: {phase}'))

    ax1.legend(handles=legend_elements, loc='best')
    fig.suptitle('Flight Profile Analysis (Auto-Downloaded Data)', fontsize=16, fontweight='bold')
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    csv_filename = 'my_flight_data.csv'
    flight_dataframe = load_and_prepare_data(csv_filename)
    if flight_dataframe is not None:
        flight_dataframe = apply_phase_identification(flight_dataframe)
        visualize_flight_data(flight_dataframe)
    else:
        print("\nCould not analyze the flight because the data could not be loaded.")