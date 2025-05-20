Call of Duty Script Manager (UI Beta)
A Python-based tool for extracting and managing hashed data from Call of Duty game scripts (GSC, CSC, Lua) and fastfiles, designed for modding purposes. The tool identifies hashes using FNV1A-based algorithms and saves results for further analysis.
Features

Game Detection: Identifies CoD games (Black Ops 3, 4, Cold War, Modern Warfare III, Black Ops 6) based on folder/file names.
Hash Extraction: Extracts hashed and unhashed words from scripts, supporting various patterns (e.g., var_, #hash_, @"hash_).
Real-Time Hash Display: Shows hash-to-string mappings from gamename_dictionary.csv or computed hashes.
GUI: Tkinter-based interface with tabs for game detection, extraction, and hash display, plus a progress bar and console.

Requirements

Python: Version 3.6 or higher.
Modules: Standard library only (tkinter, os, re, json, csv, datetime, pathlib).
Optional: gamename_dictionary.csv for known hash-to-string mappings.

To install Python:
# On Windows
Download from https://www.python.org/downloads/

# On Linux
sudo apt-get install python3

# On macOS
brew install python3

Installation

Clone the repository:git clone https://github.com/Luisete2105/CoD-brute-force-dehasher.git
cd CoD-brute-force-dehasher


Switch to the UI_Beta branch:git checkout UI_Beta


Run the tool:python main_cod_script_manager.py



Usage

Game Detection Tab:
Select a folder containing game dumps or fastfiles.
The tool detects the game (e.g., Black Ops 6) based on folder/file names.


Scripts Data Extraction Tab:
Select a folder to extract hashes.
Click "Extract Scripts Data" to process files (.gsc, .csc, .lua, etc.).
View progress via the progress bar.
Results are saved to game-specific CSV files (e.g., bo6_var.csv, mwiii_hash.csv).


Real-Time Hash Display Tab:
Enter a string to compute hashes for all supported algorithms.
Load gamename_dictionary.csv to view known hash-to-string mappings.


Console: Logs all actions (file processing, errors) at the bottom.

Hashing Explanation
The tool processes hashes using FNV1A-based algorithms, as detailed in ATE47’s HashIndex. Key points:

FNV1A Variants:
32-bit: Used in Black Ops 3 (black_ops_3_scr) and some Modern Warfare III cases (base_fnv1a_32).
63-bit: Used in Black Ops 4, Cold War, Modern Warfare III (base_fnv1a_63, iw_resources, mwii_iii_scr).
64-bit: Used in Black Ops 6 (base_fnv1a_64, black_ops_6_scr, black_ops_6_sp_scr, iw_dvars, black_ops_6_omnvars).


Secure Hashes: Modern Warfare III and Black Ops 6 use secure strings (e.g., q6n-+7=tyytg94_* for iw_dvars) inserted into strings before hashing.
Custom Hash: Black Ops 4 and Cold War use a non-FNV1A 32-bit hash (hash_bo4cw_scr).

Game-Specific Hash Usage
Based on game_specific_info.md:

Black Ops 3:
Uses black_ops_3_scr for all script hashes (var_, function_, #hash_).
Simple FNV1A-32 with an extra prime multiplication.


Black Ops 4, Cold War:
Uses hash_bo4cw_scr for script hashes, base_fnv1a_63 for resources (#hash_, script_).


Modern Warfare III:
Multiple algorithms: mwii_iii_scr for scripts, iw_resources for script_, r"hash_, %"hash_, base_fnv1a_32 for t"hash_, iw_dvars for @"hash_.


Black Ops 6:
Uses base_fnv1a_64 for #hash_, iw_resources for script_, r"hash_, %"hash_.
black_ops_6_scr (non-SP) or black_ops_6_sp_scr (SP) for &"hash_, t"hash_.
iw_dvars for @"hash_, black_ops_6_omnvars for @o"hash_ (Lua only).



See game_specific_info.md for detailed patterns and examples.
Disclaimer
This tool is for educational and modding purposes only. It is intended to assist with understanding and modifying Call of Duty game scripts within the bounds of Activision’s terms of service. The developers are not responsible for any misuse or violations of game policies.
Future Plans

Implement brute-force dehashing using C++ for performance.
Add multiprocessing and GPU-based hashing (e.g., using CUDA).
Support fastfile decompilation.
Enhance dictionary matching with gamename_dictionary.csv.

Contributing
Contributions are welcome! Please submit pull requests to the UI_Beta branch or open issues for bugs/feature requests.
License
MIT License. See LICENSE for details.
