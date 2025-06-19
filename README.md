# Flight Data Recorder "Black Box" Analyzer

This project is a Python program that automatically downloads real-world flight data, analyzes it to identify distinct flight phases (climb, cruise, descent), and visualizes the entire flight profile.

## Features
- **Automatic Data Sourcing:** Uses the `traffic` library to download real flight data from the OpenSky Network. No manual data hunting required!
- **Rules-Based Phase Identification:** Analyzes altitude and vertical speed to segment the flight into operational phases.
- **Dynamic Visualization:** Generates a clear and detailed plot of the flight's altitude and airspeed, with color-coded backgrounds for each phase.

## Example Output
![Flight Profile Analysis](https://i.imgur.com/Uu3VbSr.png)


## How to Run
1.  Clone this repository.
2.  Install the required libraries: `pip install -r requirements.txt`
3.  Run the `run_analyzer.bat` file (on Windows) or execute `python fdr_analyzer_final.py` (on Mac/Linux).
