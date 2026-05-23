"""Simulation session — stateful representation of a Geant4 simulation.

A Session holds the full description of a simulation: particle source, geometry
reference, physics list, run parameters, and scoring configuration. It can
serialize to/from JSON and emit complete .mac files.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from cli_anything.geant4.core.macro import (
    build_macro,
    run_initialize,
    run_beam_on,
    run_verbose,
    run_number_of_threads,
    run_set_cut,
    gun_particle,
    gun_energy,
    gun_direction,
    gun_position,
    gun_time,
    gun_ion,
    gun_number,
    event_verbose,
    tracking_verbose,
    tracking_store_trajectory,
    control_verbose,
    random_set_seeds,
    global_field_set_value,
    write_macro,
)


class Session:
    """Stateful Geant4 simulation session."""

    def __init__(self, name: str = "sim"):
        self.name = name
        self.source: dict[str, Any] = {
            "mode": "gun",
            "particle": "gamma",
            "energy": 1.0,
            "energy_unit": "GeV",
            "direction": [0.0, 0.0, 1.0],
            "position": [0.0, 0.0, 0.0],
            "position_unit": "cm",
        }
        self.run: dict[str, Any] = {
            "n_events": 1,
            "n_threads": 1,
            "verbose": 1,
            "event_verbose": 0,
            "tracking_verbose": 1,
            "control_verbose": 2,
        }
        self.physics: dict[str, Any] = {
            "cut": 0.7,
            "cut_unit": "mm",
            "physics_list": None,
        }
        self.scoring: list[dict[str, Any]] = []
        self.magnetic_field: Optional[dict[str, Any]] = None
        self.visualization: Optional[dict[str, Any]] = None
        self.geometry: Optional[dict[str, Any]] = None
        self.random_seeds: Optional[list[int]] = None
        self._modified = False

    # ------------------------------------------------------------------
    # Source configuration
    # ------------------------------------------------------------------

    def set_particle(self, name: str) -> dict:
        self.source["particle"] = name
        self._modified = True
        return {"particle": name}

    def set_energy(self, energy: float, unit: str = "GeV") -> dict:
        self.source["energy"] = energy
        self.source["energy_unit"] = unit
        self._modified = True
        return {"energy": energy, "unit": unit}

    def set_direction(self, ex: float, ey: float, ez: float) -> dict:
        self.source["direction"] = [ex, ey, ez]
        self._modified = True
        return {"direction": [ex, ey, ez]}

    def set_position(self, x: float, y: float, z: float, unit: str = "cm") -> dict:
        self.source["position"] = [x, y, z]
        self.source["position_unit"] = unit
        self._modified = True
        return {"position": [x, y, z], "unit": unit}

    def set_source_mode(self, mode: str) -> dict:
        if mode not in ("gun", "gps"):
            raise ValueError(f"Invalid source mode: {mode}. Use 'gun' or 'gps'.")
        self.source["mode"] = mode
        self._modified = True
        return {"mode": mode}

    def set_ion(self, z: int, a: int, q: int = 0, excitation: float = 0.0) -> dict:
        self.source["ion"] = {"z": z, "a": a, "q": q, "excitation": excitation}
        self._modified = True
        return self.source["ion"]

    # ------------------------------------------------------------------
    # Run configuration
    # ------------------------------------------------------------------

    def set_n_events(self, n: int) -> dict:
        self.run["n_events"] = n
        self._modified = True
        return {"n_events": n}

    def set_n_threads(self, n: int) -> dict:
        self.run["n_threads"] = n
        self._modified = True
        return {"n_threads": n}

    def set_verbose(self, level: int) -> dict:
        self.run["verbose"] = level
        self._modified = True
        return {"verbose": level}

    # ------------------------------------------------------------------
    # Physics configuration
    # ------------------------------------------------------------------

    def set_cut(self, cut: float, unit: str = "mm") -> dict:
        self.physics["cut"] = cut
        self.physics["cut_unit"] = unit
        self._modified = True
        return {"cut": cut, "unit": unit}

    def set_physics_list(self, name: str) -> dict:
        self.physics["physics_list"] = name
        self._modified = True
        return {"physics_list": name}

    # ------------------------------------------------------------------
    # Magnetic field
    # ------------------------------------------------------------------

    def set_magnetic_field(self, bx: float, by: float, bz: float,
                           unit: str = "tesla") -> dict:
        self.magnetic_field = {"bx": bx, "by": by, "bz": bz, "unit": unit}
        self._modified = True
        return self.magnetic_field

    def remove_magnetic_field(self) -> dict:
        self.magnetic_field = None
        self._modified = True
        return {"magnetic_field": None}

    # ------------------------------------------------------------------
    # Random
    # ------------------------------------------------------------------

    def set_random_seeds(self, *seeds: int) -> dict:
        self.random_seeds = list(seeds)
        self._modified = True
        return {"seeds": list(seeds)}

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def add_scoring_mesh(self, name: str, mesh_type: str = "box",
                         size: Optional[dict] = None,
                         n_bin: Optional[dict] = None) -> dict:
        entry = {
            "name": name,
            "type": mesh_type,
            "size": size or {},
            "n_bin": n_bin or {},
        }
        self.scoring.append(entry)
        self._modified = True
        return entry

    def list_scoring(self) -> list[dict]:
        return list(self.scoring)

    def remove_scoring(self, name: str) -> dict:
        before = len(self.scoring)
        self.scoring = [s for s in self.scoring if s["name"] != name]
        removed = before - len(self.scoring)
        self._modified = True
        return {"removed": removed}

    # ------------------------------------------------------------------
    # Macro generation
    # ------------------------------------------------------------------

    def to_macro_commands(self) -> list[str]:
        """Emit the full list of macro commands for this session."""
        cmds: list[str] = []

        # Control verbosity
        if self.run.get("control_verbose"):
            cmds.append(control_verbose(self.run["control_verbose"]))

        # Random seeds
        if self.random_seeds:
            cmds.append(random_set_seeds(*self.random_seeds))

        # Physics
        if self.physics.get("physics_list"):
            cmds.append(f"/physics_lists/factory/set {self.physics['physics_list']}")
        if self.physics.get("cut") is not None:
            cmds.append(run_set_cut(self.physics["cut"], self.physics["cut_unit"]))

        # Magnetic field
        if self.magnetic_field:
            mf = self.magnetic_field
            cmds.append(global_field_set_value(
                mf["bx"], mf["by"], mf["bz"], mf["unit"]))

        # Initialize
        cmds.append(run_initialize())

        # Source
        src = self.source
        if src["mode"] == "gun":
            cmds.append(gun_particle(src["particle"]))
            cmds.append(gun_energy(src["energy"], src["energy_unit"]))
            d = src["direction"]
            cmds.append(gun_direction(d[0], d[1], d[2]))
            p = src["position"]
            cmds.append(gun_position(p[0], p[1], p[2], src["position_unit"]))
            if "ion" in src:
                ion = src["ion"]
                cmds.append(gun_ion(ion["z"], ion["a"], ion["q"], ion["excitation"]))
        else:
            cmds.append(gps_particle(src["particle"]))
            cmds.append(gps_energy(src["energy"], src["energy_unit"]))
            d = src["direction"]
            cmds.append(gps_direction(d[0], d[1], d[2]))

        # Verbosity
        cmds.append(run_verbose(self.run["verbose"]))
        cmds.append(event_verbose(self.run["event_verbose"]))
        cmds.append(tracking_verbose(self.run["tracking_verbose"]))

        # Scoring meshes
        for mesh in self.scoring:
            if mesh["type"] == "box":
                cmds.append(score_create_box_mesh(mesh["name"]))
            else:
                cmds.append(score_create_cylinder_mesh(mesh["name"]))
            cmds.append(score_open(mesh["name"]))
            if mesh["size"]:
                s = mesh["size"]
                if "dx" in s:
                    cmds.append(score_mesh_box_size(s["dx"], s["dy"], s["dz"],
                                                    s.get("unit", "m")))
            if mesh["n_bin"]:
                nb = mesh["n_bin"]
                cmds.append(score_mesh_n_bin(nb["i"], nb["j"], nb["k"]))
            cmds.append(score_close())

        # Beam on
        cmds.append(run_beam_on(self.run["n_events"]))

        return cmds

    def to_macro(self, comments: Optional[list[str]] = None) -> str:
        return build_macro(self.to_macro_commands(), comments)

    def write_macro(self, path: str) -> str:
        comments = [
            f"Session: {self.name}",
            f"Particle: {self.source['particle']}",
            f"Energy: {self.source['energy']} {self.source['energy_unit']}",
            f"Events: {self.run['n_events']}",
        ]
        return write_macro(path, self.to_macro_commands(), comments)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source": self.source,
            "run": self.run,
            "physics": self.physics,
            "scoring": self.scoring,
            "magnetic_field": self.magnetic_field,
            "random_seeds": self.random_seeds,
            "visualization": self.visualization,
            "geometry": self.geometry,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Session:
        s = cls(name=data.get("name", "sim"))
        s.source = data.get("source", s.source)
        s.run = data.get("run", s.run)
        s.physics = data.get("physics", s.physics)
        s.scoring = data.get("scoring", [])
        s.magnetic_field = data.get("magnetic_field")
        s.random_seeds = data.get("random_seeds")
        s.visualization = data.get("visualization")
        s.geometry = data.get("geometry")
        s._modified = False
        return s

    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return os.path.abspath(path)

    @classmethod
    def load(cls, path: str) -> Session:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @property
    def modified(self) -> bool:
        return self._modified

    def status(self) -> dict:
        return {
            "name": self.name,
            "modified": self._modified,
            "source": self.source,
            "run": self.run,
            "physics": self.physics,
            "scoring_count": len(self.scoring),
            "magnetic_field": self.magnetic_field is not None,
            "random_seeds_set": self.random_seeds is not None,
        }
