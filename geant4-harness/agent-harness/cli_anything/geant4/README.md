# Geant4 CLI Harness

Agent-native CLI for Geant4 Monte Carlo particle simulation.

## Prerequisites

- **Geant4** — compiled from source or installed via conda
  - Set `GEANT4_EXECUTABLE` env var to point to a compiled example, or
  - Set `GEANT4_INSTALL_DIR` to the Geant4 install prefix
  - Build from source: https://geant4.web.cern.ch/
  - Conda: `conda install -c conda-forge geant4`

## Install

```bash
cd agent-harness
pip install -e .
```

## Usage

```bash
# Check if Geant4 is found
cli-anything-geant4 check

# Create a session and configure
cli-anything-geant4 session new --name mysim -o mysim.json
cli-anything-geant4 -s mysim.json source set -p gamma -e 6 -d 0 0 1 --energy-unit MeV
cli-anything-geant4 -s mysim.json run set -n 1000
cli-anything-geant4 -s mysim.json physics set --cut 0.7 --physics-list FTFP_BERT

# Generate macro file
cli-anything-geant4 -s mysim.json macro generate -o run.mac

# Run simulation
cli-anything-geant4 exec --macro run.mac

# Interactive REPL
cli-anything-geant4
```

## Run Tests

```bash
pip install pytest
python -m pytest cli_anything/geant4/tests/ -v
```
