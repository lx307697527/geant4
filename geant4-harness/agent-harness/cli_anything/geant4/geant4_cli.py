"""Geant4 CLI — agent-native command-line interface for Geant4 simulation.

Provides subcommand and REPL access to Geant4 macro generation, simulation
execution, and output parsing.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import click

from cli_anything.geant4.core.session import Session
from cli_anything.geant4.utils.geant4_backend import (
    check_installation,
    run_simulation,
    find_geant4_executable,
)
from cli_anything.geant4.utils.output import output_json, output_table


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

_session: Optional[Session] = None
_session_file: Optional[str] = None


def _get_session(ctx: click.Context) -> Session:
    global _session
    if _session is None:
        sf = ctx.obj.get("session_file") if ctx.obj else None
        if sf and os.path.isfile(sf):
            _session = Session.load(sf)
        else:
            _session = Session()
    return _session


def _save_session(ctx: click.Context) -> None:
    sf = ctx.obj.get("session_file") if ctx.obj else None
    if sf and _session is not None:
        _session.save(sf)


def _output(ctx: click.Context, data: dict) -> None:
    if ctx.obj and ctx.obj.get("json"):
        output_json(data)
    else:
        for k, v in data.items():
            click.echo(f"  {k}: {v}")


def _handle_exc(ctx: click.Context, exc: Exception) -> None:
    if ctx.obj and ctx.obj.get("json"):
        output_json({"error": str(exc), "type": type(exc).__name__})
    else:
        raise click.ClickException(str(exc))


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output in JSON format.")
@click.option("--session-file", "-s", type=click.Path(), help="Session file path.")
@click.option("--version", is_flag=True, help="Show version.")
@click.pass_context
def cli(ctx, use_json, session_file, version):
    """cli-anything-geant4 — Agent-native CLI for Geant4 simulation."""
    if version:
        from cli_anything.geant4 import __version__
        click.echo(f"cli-anything-geant4 {__version__}")
        return

    ctx.ensure_object(dict)
    ctx.obj["json"] = use_json
    ctx.obj["session_file"] = session_file

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

@cli.command()
@click.pass_context
def repl(ctx):
    """Interactive REPL for Geant4 simulation control."""
    try:
        from cli_anything.geant4.utils.repl_skin import ReplSkin
        skin = ReplSkin("geant4", version="0.1.0")
        skin.print_banner()

        commands_map = {
            "source": "Particle source configuration",
            "run": "Run control (n_events, threads, verbose)",
            "physics": "Physics list and cuts",
            "field": "Magnetic field configuration",
            "score": "Scoring mesh management",
            "macro": "Generate and write macro files",
            "exec": "Run a simulation",
            "session": "Session save/load/status",
            "check": "Check Geant4 installation",
            "help": "Show this help",
            "quit": "Exit REPL",
        }
        skin.help(commands_map)

        try:
            pt_session = skin.create_prompt_session()
        except Exception:
            pt_session = None

        while True:
            try:
                if pt_session:
                    line = skin.get_input(pt_session)
                else:
                    line = input("geant4> ").strip()
                if not line:
                    continue
                if line.lower() in ("quit", "exit", "q"):
                    break
                if line.lower() == "help":
                    skin.help(commands_map)
                    continue
                cli.main(line.split(), standalone_mode=False,
                         obj=ctx.obj.copy())
            except (EOFError, KeyboardInterrupt):
                break
            except SystemExit:
                continue
            except click.ClickException as e:
                skin.error(str(e))
            except Exception as e:
                skin.error(f"{type(e).__name__}: {e}")

        skin.print_goodbye()
    except ImportError:
        click.echo("Geant4 REPL (prompt_toolkit not available, using basic mode)")
        while True:
            try:
                line = input("geant4> ").strip()
                if not line:
                    continue
                if line.lower() in ("quit", "exit", "q"):
                    break
                cli.main(line.split(), standalone_mode=False,
                         obj=ctx.obj.copy())
            except (EOFError, KeyboardInterrupt):
                break
            except SystemExit:
                continue
            except click.ClickException as e:
                click.echo(f"Error: {e}")


# ---------------------------------------------------------------------------
# Source command group
# ---------------------------------------------------------------------------

@cli.group()
@click.pass_context
def source(ctx):
    """Particle source configuration."""
    pass


@source.command("set")
@click.option("--particle", "-p", help="Particle name (gamma, proton, e-, etc.)")
@click.option("--energy", "-e", type=float, help="Kinetic energy")
@click.option("--energy-unit", default="GeV", help="Energy unit (default: GeV)")
@click.option("--direction", "-d", nargs=3, type=float, help="Direction (ex ey ez)")
@click.option("--position", nargs=3, type=float, help="Position (x y z)")
@click.option("--position-unit", default="cm", help="Position unit (default: cm)")
@click.option("--mode", type=click.Choice(["gun", "gps"]), help="Source mode")
@click.pass_context
def source_set(ctx, particle, energy, energy_unit, direction, position,
               position_unit, mode):
    """Set particle source parameters."""
    sess = _get_session(ctx)
    results = {}
    if mode:
        results.update(sess.set_source_mode(mode))
    if particle:
        results.update(sess.set_particle(particle))
    if energy is not None:
        results.update(sess.set_energy(energy, energy_unit))
    if direction:
        results.update(sess.set_direction(*direction))
    if position:
        results.update(sess.set_position(*position, unit=position_unit))
    _save_session(ctx)
    _output(ctx, results)


@source.command("info")
@click.pass_context
def source_info(ctx):
    """Show current source configuration."""
    sess = _get_session(ctx)
    _output(ctx, sess.source)


# ---------------------------------------------------------------------------
# Run command group
# ---------------------------------------------------------------------------

@cli.group()
@click.pass_context
def run(ctx):
    """Run control parameters."""
    pass


@run.command("set")
@click.option("--n-events", "-n", type=int, help="Number of events to simulate")
@click.option("--n-threads", "-t", type=int, help="Number of threads")
@click.option("--verbose", "-v", type=int, help="Run verbosity level")
@click.pass_context
def run_set(ctx, n_events, n_threads, verbose):
    """Set run parameters."""
    sess = _get_session(ctx)
    results = {}
    if n_events is not None:
        results.update(sess.set_n_events(n_events))
    if n_threads is not None:
        results.update(sess.set_n_threads(n_threads))
    if verbose is not None:
        results.update(sess.set_verbose(verbose))
    _save_session(ctx)
    _output(ctx, results)


@run.command("info")
@click.pass_context
def run_info(ctx):
    """Show current run configuration."""
    sess = _get_session(ctx)
    _output(ctx, sess.run)


# ---------------------------------------------------------------------------
# Physics command group
# ---------------------------------------------------------------------------

@cli.group()
@click.pass_context
def physics(ctx):
    """Physics list and production cuts."""
    pass


@physics.command("set")
@click.option("--cut", type=float, help="Default production cut")
@click.option("--cut-unit", default="mm", help="Cut unit (default: mm)")
@click.option("--physics-list", help="Physics list name (e.g. FTFP_BERT)")
@click.pass_context
def physics_set(ctx, cut, cut_unit, physics_list):
    """Set physics parameters."""
    sess = _get_session(ctx)
    results = {}
    if cut is not None:
        results.update(sess.set_cut(cut, cut_unit))
    if physics_list:
        results.update(sess.set_physics_list(physics_list))
    _save_session(ctx)
    _output(ctx, results)


@physics.command("info")
@click.pass_context
def physics_info(ctx):
    """Show current physics configuration."""
    sess = _get_session(ctx)
    _output(ctx, sess.physics)


# ---------------------------------------------------------------------------
# Field command group
# ---------------------------------------------------------------------------

@cli.group("field")
@click.pass_context
def field(ctx):
    """Magnetic field configuration."""
    pass


@field.command("set")
@click.option("--bx", type=float, required=True, help="Bx component")
@click.option("--by", type=float, required=True, help="By component")
@click.option("--bz", type=float, required=True, help="Bz component")
@click.option("--unit", default="tesla", help="Field unit (default: tesla)")
@click.pass_context
def field_set(ctx, bx, by, bz, unit):
    """Set global magnetic field."""
    sess = _get_session(ctx)
    result = sess.set_magnetic_field(bx, by, bz, unit)
    _save_session(ctx)
    _output(ctx, result)


@field.command("remove")
@click.pass_context
def field_remove(ctx):
    """Remove magnetic field."""
    sess = _get_session(ctx)
    result = sess.remove_magnetic_field()
    _save_session(ctx)
    _output(ctx, result)


# ---------------------------------------------------------------------------
# Score command group
# ---------------------------------------------------------------------------

@cli.group("score")
@click.pass_context
def score(ctx):
    """Scoring mesh management."""
    pass


@score.command("add")
@click.option("--name", required=True, help="Mesh name")
@click.option("--type", "mesh_type", type=click.Choice(["box", "cylinder"]),
              default="box", help="Mesh type")
@click.option("--size", nargs=3, type=float, help="Mesh size (dx dy dz)")
@click.option("--size-unit", default="m", help="Size unit")
@click.option("--n-bin", nargs=3, type=int, help="Number of bins (i j k)")
@click.pass_context
def score_add(ctx, name, mesh_type, size, size_unit, n_bin):
    """Add a scoring mesh."""
    sess = _get_session(ctx)
    size_dict = None
    if size:
        size_dict = {"dx": size[0], "dy": size[1], "dz": size[2],
                     "unit": size_unit}
    nbin_dict = None
    if n_bin:
        nbin_dict = {"i": n_bin[0], "j": n_bin[1], "k": n_bin[2]}
    result = sess.add_scoring_mesh(name, mesh_type, size_dict, nbin_dict)
    _save_session(ctx)
    _output(ctx, result)


@score.command("list")
@click.pass_context
def score_list(ctx):
    """List scoring meshes."""
    sess = _get_session(ctx)
    result = sess.list_scoring()
    if ctx.obj and ctx.obj.get("json"):
        output_json(result)
    else:
        output_table(result, ["name", "type"])


@score.command("remove")
@click.argument("name")
@click.pass_context
def score_remove(ctx, name):
    """Remove a scoring mesh by name."""
    sess = _get_session(ctx)
    result = sess.remove_scoring(name)
    _save_session(ctx)
    _output(ctx, result)


# ---------------------------------------------------------------------------
# Macro command group
# ---------------------------------------------------------------------------

@cli.group("macro")
@click.pass_context
def macro(ctx):
    """Generate and write macro files."""
    pass


@macro.command("generate")
@click.option("--output", "-o", type=click.Path(), help="Output .mac file path")
@click.pass_context
def macro_generate(ctx, output):
    """Generate macro file from current session."""
    sess = _get_session(ctx)
    if output:
        path = sess.write_macro(output)
        result = {"path": path, "status": "written"}
    else:
        content = sess.to_macro()
        result = {"content": content, "status": "generated"}
    _output(ctx, result)


@macro.command("validate")
@click.argument("macro_path", type=click.Path(exists=True))
@click.pass_context
def macro_validate(ctx, macro_path):
    """Validate a .mac file syntax (basic checks)."""
    with open(macro_path, encoding="utf-8") as f:
        lines = f.readlines()

    errors = []
    known_prefixes = {
        "/run/", "/gun/", "/gps/", "/event/", "/tracking/", "/process/",
        "/control/", "/random/", "/vis/", "/score/", "/hits/", "/material/",
        "/globalField/", "/physics_lists/", "/particle/", "/cuts/",
        "/adjoint/", "/polarization/", "/param/", "/units/", "/gui/",
    }

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not any(stripped.startswith(p) for p in known_prefixes):
            if not stripped.startswith("/"):
                errors.append({"line": i, "content": stripped,
                               "issue": "Does not start with /"})

    result = {
        "file": macro_path,
        "total_lines": len(lines),
        "errors": errors,
        "valid": len(errors) == 0,
    }
    _output(ctx, result)


# ---------------------------------------------------------------------------
# Exec command
# ---------------------------------------------------------------------------

@cli.command("exec")
@click.option("--executable", help="Geant4 executable name or path")
@click.option("--macro", "-m", type=click.Path(exists=True),
              help="Macro file to execute")
@click.option("--n-threads", "-t", type=int, help="Number of threads")
@click.option("--output-dir", type=click.Path(), help="Working directory")
@click.option("--timeout", type=int, default=3600,
              help="Timeout in seconds (default: 3600)")
@click.pass_context
def exec_cmd(ctx, executable, macro, n_threads, output_dir, timeout):
    """Run a Geant4 simulation."""
    try:
        result = run_simulation(
            executable=executable,
            macro=macro,
            n_threads=n_threads,
            output_dir=output_dir,
            timeout=timeout,
        )
        _output(ctx, result)
    except Exception as exc:
        _handle_exc(ctx, exc)


# ---------------------------------------------------------------------------
# Session command group
# ---------------------------------------------------------------------------

@cli.group("session")
@click.pass_context
def session(ctx):
    """Session management (save, load, status)."""
    pass


@session.command("new")
@click.option("--name", default="sim", help="Session name")
@click.option("--output", "-o", type=click.Path(), help="Save to file")
@click.pass_context
def session_new(ctx, name, output):
    """Create a new simulation session."""
    global _session
    _session = Session(name=name)
    result = _session.status()
    if output:
        path = _session.save(output)
        result["saved_to"] = path
        ctx.obj["session_file"] = output
    _output(ctx, result)


@session.command("save")
@click.option("--output", "-o", type=click.Path(), help="Save to file")
@click.pass_context
def session_save(ctx, output):
    """Save current session."""
    sess = _get_session(ctx)
    sf = output or ctx.obj.get("session_file")
    if not sf:
        raise click.ClickException("No session file specified. Use -o or --session-file.")
    path = sess.save(sf)
    _output(ctx, {"saved_to": path})


@session.command("load")
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def session_load(ctx, path):
    """Load a session from file."""
    global _session, _session_file
    _session = Session.load(path)
    _session_file = path
    ctx.obj["session_file"] = path
    _output(ctx, _session.status())


@session.command("status")
@click.pass_context
def session_status(ctx):
    """Show current session status."""
    sess = _get_session(ctx)
    _output(ctx, sess.status())


# ---------------------------------------------------------------------------
# Check command
# ---------------------------------------------------------------------------

@cli.command("check")
@click.pass_context
def check(ctx):
    """Check Geant4 installation status."""
    result = check_installation()
    _output(ctx, result)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    cli()


if __name__ == "__main__":
    main()
