---
name: "cli-anything-geant4"
description: "Agent-native CLI for Geant4 Monte Carlo simulation — generate macros, configure runs, execute simulations"
---

# cli-anything-geant4

Agent-native CLI harness for Geant4 Monte Carlo particle simulation toolkit.

## Prerequisites

- Geant4 compiled and installed (set `GEANT4_EXECUTABLE` or `GEANT4_INSTALL_DIR`)
- Python >= 3.10

## Installation

```bash
pip install cli-anything-geant4
```

## Command Groups

| Group | Description |
|-------|-------------|
| `source` | Particle source configuration (type, energy, direction, position) |
| `run` | Run parameters (n_events, threads, verbosity) |
| `physics` | Physics list and production cuts |
| `field` | Global magnetic field |
| `score` | Scoring mesh management |
| `macro` | Generate/validate .mac files |
| `exec` | Execute a Geant4 simulation |
| `session` | Session save/load/status |
| `check` | Verify Geant4 installation |

## Common Workflows

### Configure and run a gamma simulation

```bash
# JSON output for agent consumption
cli-anything-geant4 --json session new --name dose -o dose.json
cli-anything-geant4 --json -s dose.json source set -p gamma -e 6 --energy-unit MeV
cli-anything-geant4 --json -s dose.json source set -d 0 0 1
cli-anything-geant4 --json -s dose.json run set -n 10000 -t 4
cli-anything-geant4 --json -s dose.json macro generate -o run.mac
cli-anything-geant4 --json exec --macro run.mac -t 4
```

### Use General Particle Source (GPS)

```bash
cli-anything-geant4 -s sim.json source set --mode gps -p proton -e 210 --energy-unit MeV
```

### Add scoring mesh

```bash
cli-anything-geant4 -s sim.json score add --name dose_mesh --type box --size 10 10 10 --n-bin 50 50 50
```

### Validate macro file

```bash
cli-anything-geant4 --json macro validate run.mac
```

## Agent Guidance

- Use `--json` flag for machine-readable output
- `check` command verifies Geant4 availability before running
- `macro generate` creates .mac files without requiring Geant4 installed
- `exec` requires Geant4 executable — use `GEANT4_EXECUTABLE` env var
- Sessions serialize to JSON and can be saved/loaded across invocations
