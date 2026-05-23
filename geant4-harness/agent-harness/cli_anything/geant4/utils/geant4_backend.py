"""Geant4 backend — discover and invoke the Geant4 executable.

This module finds a compiled Geant4 application on the system and runs
simulation macros through it.  The backend is a hard dependency — if no
Geant4 executable is found, commands fail with clear install instructions.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Optional


def find_geant4_executable(name: Optional[str] = None) -> str:
    """Locate a Geant4 executable.

    Search order:
    1. GEANT4_EXECUTABLE env var
    2. ``name`` argument (if provided)
    3. Common executable names on PATH (exampleB1, exampleN02, etc.)
    4. GEANT4_INSTALL_DIR/examples build directories

    Returns:
        Absolute path to the executable.

    Raises:
        RuntimeError: If no executable can be found.
    """
    # 1. Environment variable
    env_exe = os.environ.get("GEANT4_EXECUTABLE")
    if env_exe and os.path.isfile(env_exe):
        return env_exe

    # 2. Explicit name
    if name:
        found = shutil.which(name)
        if found:
            return found
        if os.path.isfile(name):
            return os.path.abspath(name)

    # 3. Common example names
    for candidate in ("exampleB1", "exampleN02", "exampleN03", "exampleN04"):
        found = shutil.which(candidate)
        if found:
            return found

    # 4. Install dir
    install_dir = os.environ.get("GEANT4_INSTALL_DIR", "")
    if install_dir:
        for root, _dirs, files in os.walk(install_dir):
            for f in files:
                if f.startswith("example") and not f.endswith(".cc"):
                    return os.path.join(root, f)

    raise RuntimeError(
        "Geant4 executable not found. Install Geant4 and set "
        "GEANT4_EXECUTABLE or GEANT4_INSTALL_DIR, or compile an example "
        "and add it to PATH.\n"
        "Build from source: https://geant4.web.cern.ch/\n"
        "Or via conda: conda install -c conda-forge geant4"
    )


def run_simulation(
    executable: Optional[str] = None,
    macro: Optional[str] = None,
    n_threads: Optional[int] = None,
    output_dir: Optional[str] = None,
    timeout: Optional[int] = None,
) -> dict:
    """Run a Geant4 simulation.

    Args:
        executable: Path or name of the Geant4 executable.
        macro: Path to the .mac file to execute.
        n_threads: Number of threads (passed before macro path).
        output_dir: Working directory for the simulation.
        timeout: Maximum runtime in seconds.

    Returns:
        Dict with returncode, stdout, stderr, and metadata.
    """
    exe = find_geant4_executable(executable)

    cmd = [exe]
    if n_threads and n_threads > 1:
        cmd.extend(["-t", str(n_threads)])
    if macro:
        cmd.append(macro)

    cwd = output_dir or os.getcwd()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "executable": exe,
            "macro": macro,
            "cwd": cwd,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Simulation timed out after {timeout}s",
            "executable": exe,
            "macro": macro,
            "cwd": cwd,
            "success": False,
            "timeout": True,
        }
    except FileNotFoundError:
        raise RuntimeError(
            f"Geant4 executable not found: {exe}\n"
            "Ensure Geant4 is compiled and the executable path is correct."
        )


def check_installation() -> dict:
    """Check whether Geant4 is available on the system.

    Returns a dict with availability status and discovered paths.
    """
    result = {
        "installed": False,
        "executable": None,
        "geant4_dir": os.environ.get("GEANT4_INSTALL_DIR"),
        "geant4_data": os.environ.get("G4DATA"),
    }

    try:
        exe = find_geant4_executable()
        result["installed"] = True
        result["executable"] = exe
    except RuntimeError:
        pass

    return result


def list_examples(install_dir: Optional[str] = None) -> list[dict]:
    """Scan for compiled Geant4 example executables.

    Returns a list of dicts with name and path for each found example.
    """
    search_dir = install_dir or os.environ.get("GEANT4_INSTALL_DIR", "")
    examples: list[dict] = []

    if not search_dir or not os.path.isdir(search_dir):
        return examples

    for root, _dirs, files in os.walk(search_dir):
        for f in files:
            if f.startswith("example") and not f.endswith((".cc", ".cpp", ".hh")):
                full = os.path.join(root, f)
                if os.access(full, os.X_OK) or full.endswith(".exe"):
                    examples.append({"name": f, "path": full})

    return examples
