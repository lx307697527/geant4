"""Geant4 macro file generator.

Builds valid .mac files from structured Python data. Each generator function
returns a list of macro command strings that can be joined and written to disk.
"""

from __future__ import annotations

from typing import Optional


def _cmd(path: str, *args: str) -> str:
    parts = [path] + [str(a) for a in args if a is not None]
    return "/".join(parts)


# ---------------------------------------------------------------------------
# Run control
# ---------------------------------------------------------------------------

def run_initialize() -> str:
    return "/run/initialize"


def run_beam_on(n_events: int, macro_file: Optional[str] = None,
                n_select: Optional[int] = None) -> str:
    parts = [str(n_events)]
    if macro_file:
        parts.append(macro_file)
        if n_select is not None:
            parts.append(str(n_select))
    return f"/run/beamOn {' '.join(parts)}"


def run_verbose(level: int) -> str:
    return f"/run/verbose {level}"


def run_number_of_threads(n: int) -> str:
    return f"/run/numberOfThreads {n}"


def run_abort(soft: bool = False) -> str:
    return f"/run/abort {'true' if soft else 'false'}"


def run_geometry_modified() -> str:
    return "/run/geometryModified"


def run_physics_modified() -> str:
    return "/run/physicsModified"


def run_set_cut(cut: float, unit: str = "mm") -> str:
    return f"/run/setCut {cut} {unit}"


def run_set_cut_for_particle(particle: str, cut: float, unit: str = "mm") -> str:
    return f"/run/setCutForAGivenParticle {particle} {cut} {unit}"


# ---------------------------------------------------------------------------
# Particle gun (/gun/)
# ---------------------------------------------------------------------------

def gun_particle(name: str) -> str:
    return f"/gun/particle {name}"


def gun_energy(energy: float, unit: str = "GeV") -> str:
    return f"/gun/energy {energy} {unit}"


def gun_direction(ex: float, ey: float, ez: float) -> str:
    return f"/gun/direction {ex} {ey} {ez}"


def gun_position(x: float, y: float, z: float, unit: str = "cm") -> str:
    return f"/gun/position {x} {y} {z} {unit}"


def gun_momentum(px: float, py: float, pz: float, unit: str = "GeV") -> str:
    return f"/gun/momentum {px} {py} {pz} {unit}"


def gun_time(t0: float, unit: str = "ns") -> str:
    return f"/gun/time {t0} {unit}"


def gun_polarization(px: float, py: float, pz: float) -> str:
    return f"/gun/polarization {px} {py} {pz}"


def gun_number(n: int) -> str:
    return f"/gun/number {n}"


def gun_ion(z: int, a: int, q: int = 0, excitation: float = 0.0) -> str:
    parts = [str(z), str(a)]
    if q or excitation:
        parts.append(str(q))
    if excitation:
        parts.append(str(excitation))
    return f"/gun/ion {' '.join(parts)}"


# ---------------------------------------------------------------------------
# GPS (/gps/) — General Particle Source
# ---------------------------------------------------------------------------

def gps_particle(name: str) -> str:
    return f"/gps/particle {name}"


def gps_energy(energy: float, unit: str = "GeV") -> str:
    return f"/gps/energy {energy} {unit}"


def gps_direction(px: float, py: float, pz: float) -> str:
    return f"/gps/direction {px} {py} {pz}"


def gps_position(x: float, y: float, z: float, unit: str = "cm") -> str:
    return f"/gps/position {x} {y} {z} {unit}"


def gps_pos_type(pos_type: str) -> str:
    return f"/gps/pos/type {pos_type}"


def gps_pos_shape(shape: str) -> str:
    return f"/gps/pos/shape {shape}"


def gps_pos_centre(x: float, y: float, z: float, unit: str = "cm") -> str:
    return f"/gps/pos/centre {x} {y} {z} {unit}"


def gps_pos_radius(r: float, unit: str = "cm") -> str:
    return f"/gps/pos/radius {r} {unit}"


def gps_pos_halfx(hx: float, unit: str = "cm") -> str:
    return f"/gps/pos/halfx {hx} {unit}"


def gps_pos_halfy(hy: float, unit: str = "cm") -> str:
    return f"/gps/pos/halfy {hy} {unit}"


def gps_pos_halfz(hz: float, unit: str = "cm") -> str:
    return f"/gps/pos/halfz {hz} {unit}"


def gps_pos_confine(vol_name: str) -> str:
    return f"/gps/pos/confine {vol_name}"


def gps_ang_type(ang_type: str) -> str:
    return f"/gps/ang/type {ang_type}"


def gps_ang_mintheta(theta: float, unit: str = "rad") -> str:
    return f"/gps/ang/mintheta {theta} {unit}"


def gps_ang_maxtheta(theta: float, unit: str = "rad") -> str:
    return f"/gps/ang/maxtheta {theta} {unit}"


def gps_ang_minphi(phi: float, unit: str = "rad") -> str:
    return f"/gps/ang/minphi {phi} {unit}"


def gps_ang_maxphi(phi: float, unit: str = "rad") -> str:
    return f"/gps/ang/maxphi {phi} {unit}"


def gps_ang_focuspoint(x: float, y: float, z: float, unit: str = "cm") -> str:
    return f"/gps/ang/focuspoint {x} {y} {z} {unit}"


def gps_ene_type(ene_type: str) -> str:
    return f"/gps/ene/type {ene_type}"


def gps_ene_mono(energy: float, unit: str = "GeV") -> str:
    return f"/gps/ene/mono {energy} {unit}"


def gps_ene_min(emin: float, unit: str = "GeV") -> str:
    return f"/gps/ene/min {emin} {unit}"


def gps_ene_max(emax: float, unit: str = "GeV") -> str:
    return f"/gps/ene/max {emax} {unit}"


def gps_ene_sigma(sigma: float, unit: str = "GeV") -> str:
    return f"/gps/ene/sigma {sigma} {unit}"


def gps_ene_alpha(alpha: float) -> str:
    return f"/gps/ene/alpha {alpha}"


def gps_source_add(intensity: float) -> str:
    return f"/gps/source/add {intensity}"


def gps_verbose(level: int) -> str:
    return f"/gps/verbose {level}"


# ---------------------------------------------------------------------------
# Event / tracking / process
# ---------------------------------------------------------------------------

def event_verbose(level: int) -> str:
    return f"/event/verbose {level}"


def tracking_verbose(level: int) -> str:
    return f"/tracking/verbose {level}"


def tracking_store_trajectory(level: int) -> str:
    return f"/tracking/storeTrajectory {level}"


def process_list(ptype: str = "all") -> str:
    return f"/process/list {ptype}"


def process_activate(name: str, particle: Optional[str] = None) -> str:
    parts = [name]
    if particle:
        parts.append(particle)
    return f"/process/activate {' '.join(parts)}"


def process_inactivate(name: str, particle: Optional[str] = None) -> str:
    parts = [name]
    if particle:
        parts.append(particle)
    return f"/process/inactivate {' '.join(parts)}"


# ---------------------------------------------------------------------------
# Control / scripting
# ---------------------------------------------------------------------------

def control_execute(filename: str) -> str:
    return f"/control/execute {filename}"


def control_loop(macro: str, counter: str, init_val: float,
                 final_val: float, step: Optional[float] = None) -> str:
    parts = [macro, counter, str(init_val), str(final_val)]
    if step is not None:
        parts.append(str(step))
    return f"/control/loop {' '.join(parts)}"


def control_foreach(macro: str, counter: str, values: list[str]) -> str:
    return f"/control/foreach {macro} {counter} {' '.join(values)}"


def control_verbose(level: int) -> str:
    return f"/control/verbose {level}"


def control_echo(text: str) -> str:
    return f"/control/echo {text}"


# ---------------------------------------------------------------------------
# Random
# ---------------------------------------------------------------------------

def random_set_seeds(*seeds: int) -> str:
    return f"/random/setSeeds {' '.join(str(s) for s in seeds)}"


def random_set_saving_flag(flag: bool) -> str:
    return f"/random/setSavingFlag {'true' if flag else 'false'}"


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def vis_open(system: str = "OGL") -> str:
    return f"/vis/open {system}"


def vis_draw_volume(depth: Optional[int] = None) -> str:
    if depth is not None:
        return f"/vis/drawVolume {depth}"
    return "/vis/drawVolume"


def vis_verbose(level: str) -> str:
    return f"/vis/verbose {level}"


def vis_viewer_set_viewpoint_vector(x: float, y: float, z: float) -> str:
    return f"/vis/viewer/set/viewpointVector {x} {y} {z}"


def vis_viewer_set_style(style: str) -> str:
    return f"/vis/viewer/set/style {style}"


def vis_scene_add_trajectories(style: str = "smooth") -> str:
    return f"/vis/scene/add/trajectories {style}"


def vis_scene_add_hits() -> str:
    return "/vis/scene/add/hits"


def vis_scene_end_of_event_action(action: str) -> str:
    return f"/vis/scene/endOfEventAction {action}"


def vis_geometry_set_visibility(name: str, copy_no: int, flag: bool) -> str:
    return f"/vis/geometry/set/visibility {name} {copy_no} {'true' if flag else 'false'}"


def vis_geometry_set_colour(name: str, copy_no: int,
                            r: float, g: float, b: float, alpha: float = 1.0) -> str:
    parts = [name, str(copy_no), str(r), str(g), str(b)]
    if alpha < 1.0:
        parts.append(str(alpha))
    return f"/vis/geometry/set/colour {' '.join(parts)}"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_create_box_mesh(name: str) -> str:
    return f"/score/create/boxMesh {name}"


def score_create_cylinder_mesh(name: str) -> str:
    return f"/score/create/cylinderMesh {name}"


def score_open(name: str) -> str:
    return f"/score/open {name}"


def score_close() -> str:
    return "/score/close"


def score_list() -> str:
    return "/score/list"


def score_dump() -> str:
    return "/score/dump"


def score_mesh_box_size(dx: float, dy: float, dz: float, unit: str = "m") -> str:
    return f"/score/mesh/boxSize {dx} {dy} {dz} {unit}"


def score_mesh_n_bin(ni: int, nj: int, nk: int) -> str:
    return f"/score/mesh/nBin {ni} {nj} {nk}"


# ---------------------------------------------------------------------------
# Magnetic field
# ---------------------------------------------------------------------------

def global_field_set_value(bx: float, by: float, bz: float, unit: str = "tesla") -> str:
    return f"/globalField/setValue {bx} {by} {bz} {unit}"


# ---------------------------------------------------------------------------
# Composite macro builder
# ---------------------------------------------------------------------------

def build_macro(commands: list[str], comments: Optional[list[str]] = None) -> str:
    """Build a complete .mac file from a list of command strings.

    Args:
        commands: List of Geant4 macro command strings.
        comments: Optional list of comment lines to prepend.

    Returns:
        Complete macro file content as a string.
    """
    lines: list[str] = []
    if comments:
        for c in comments:
            lines.append(f"# {c}")
        lines.append("")
    for cmd in commands:
        lines.append(cmd)
    return "\n".join(lines) + "\n"


def write_macro(path: str, commands: list[str],
                comments: Optional[list[str]] = None) -> str:
    """Write a .mac file and return its absolute path."""
    import os
    content = build_macro(commands, comments)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return os.path.abspath(path)
