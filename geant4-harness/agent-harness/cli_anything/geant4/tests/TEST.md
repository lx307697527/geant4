# Geant4 CLI Harness — Test Documentation

## Test Inventory

| File | Type | Count |
|------|------|-------|
| test_core.py | Unit | ~40 |
| test_full_e2e.py | E2E (requires Geant4) | Planned |

## Unit Test Plan

### Macro Generation (test_core.py: TestMacroGeneration)
- All `run/` commands: initialize, beamOn, verbose, setCut
- All `gun/` commands: particle, energy, direction, position
- All `gps/` commands: particle, energy, pos/type, pos/shape, ang/type, ene/type
- `process/` commands: list, activate, inactivate
- `control/` commands: execute, loop
- `random/` commands: setSeeds
- `vis/` commands: open, drawVolume
- `score/` commands: createBoxMesh
- `globalField/` commands: setValue
- Composite: build_macro, write_macro

### Session (test_core.py: TestSession)
- Default and named creation
- Source configuration: particle, energy, direction, position, mode, ion
- Run configuration: n_events, n_threads, verbose
- Physics configuration: cut, physics_list
- Magnetic field: set, remove
- Random seeds
- Scoring: add, list, remove
- Macro generation: to_macro_commands, to_macro
- Serialization: save/load, to_dict/from_dict
- Modified flag tracking

### Backend (test_core.py: TestBackend)
- check_installation
- find_geant4_executable (with/without env var)

### CLI (test_core.py: TestCLI)
- --help, --version
- check command
- session new/save/load
- source set/info
- macro generate/validate
- JSON output mode

## E2E Test Plan (requires compiled Geant4)

E2E tests require a working Geant4 installation with compiled examples.

### Workflow 1: Basic gamma simulation
- Create session, configure gamma source at 6 MeV
- Generate macro, run with exampleB1
- Verify output file exists

### Workflow 2: Proton therapy beam
- Configure proton at 210 MeV with GPS
- Add scoring mesh for dose
- Run simulation, verify scoring output

### Workflow 3: Magnetic field deflection
- Set magnetic field
- Run and verify different trajectory patterns

## Test Results

(To be filled after running tests with a Geant4 installation)
