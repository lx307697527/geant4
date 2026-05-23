"""Unit tests for Geant4 CLI harness — core modules."""

import json
import os
import tempfile

import pytest

from cli_anything.geant4.core.macro import (
    run_initialize,
    run_beam_on,
    run_verbose,
    run_set_cut,
    gun_particle,
    gun_energy,
    gun_direction,
    gun_position,
    gps_particle,
    gps_energy,
    gps_pos_type,
    gps_pos_shape,
    gps_ang_type,
    gps_ene_type,
    event_verbose,
    tracking_verbose,
    process_list,
    process_activate,
    process_inactivate,
    control_execute,
    control_loop,
    random_set_seeds,
    vis_open,
    vis_draw_volume,
    score_create_box_mesh,
    score_open,
    score_close,
    global_field_set_value,
    build_macro,
    write_macro,
)
from cli_anything.geant4.core.session import Session


# ---------------------------------------------------------------------------
# Macro generation tests
# ---------------------------------------------------------------------------

class TestMacroGeneration:
    def test_run_initialize(self):
        assert run_initialize() == "/run/initialize"

    def test_run_beam_on(self):
        assert run_beam_on(100) == "/run/beamOn 100"

    def test_run_beam_on_with_macro(self):
        assert run_beam_on(100, "post.mac", 5) == "/run/beamOn 100 post.mac 5"

    def test_run_verbose(self):
        assert run_verbose(2) == "/run/verbose 2"

    def test_run_set_cut(self):
        assert run_set_cut(0.7, "mm") == "/run/setCut 0.7 mm"

    def test_gun_particle(self):
        assert gun_particle("gamma") == "/gun/particle gamma"

    def test_gun_energy(self):
        assert gun_energy(6.0, "MeV") == "/gun/energy 6.0 MeV"

    def test_gun_direction(self):
        assert gun_direction(0, 0, 1) == "/gun/direction 0 0 1"

    def test_gun_position(self):
        assert gun_position(0, 0, 0, "cm") == "/gun/position 0 0 0 cm"

    def test_gps_particle(self):
        assert gps_particle("proton") == "/gps/particle proton"

    def test_gps_energy(self):
        assert gps_energy(210, "MeV") == "/gps/energy 210 MeV"

    def test_gps_pos_type(self):
        assert gps_pos_type("Beam") == "/gps/pos/type Beam"

    def test_gps_pos_shape(self):
        assert gps_pos_shape("Circle") == "/gps/pos/shape Circle"

    def test_gps_ang_type(self):
        assert gps_ang_type("iso") == "/gps/ang/type iso"

    def test_gps_ene_type(self):
        assert gps_ene_type("Gauss") == "/gps/ene/type Gauss"

    def test_process_list(self):
        assert process_list() == "/process/list all"

    def test_process_activate(self):
        assert process_activate("msc") == "/process/activate msc"

    def test_process_activate_with_particle(self):
        assert process_activate("msc", "e-") == "/process/activate msc e-"

    def test_process_inactivate(self):
        assert process_inactivate("msc") == "/process/inactivate msc"

    def test_control_execute(self):
        assert control_execute("run.mac") == "/control/execute run.mac"

    def test_control_loop(self):
        result = control_loop("scan.mac", "E", 1.0, 10.0, 1.0)
        assert result == "/control/loop scan.mac E 1.0 10.0 1.0"

    def test_random_set_seeds(self):
        assert random_set_seeds(42, 123) == "/random/setSeeds 42 123"

    def test_vis_open(self):
        assert vis_open("OGL") == "/vis/open OGL"

    def test_vis_draw_volume(self):
        assert vis_draw_volume() == "/vis/drawVolume"

    def test_score_create_box_mesh(self):
        assert score_create_box_mesh("dose") == "/score/create/boxMesh dose"

    def test_global_field(self):
        result = global_field_set_value(0, 0, 3.0, "tesla")
        assert result == "/globalField/setValue 0 0 3.0 tesla"

    def test_build_macro(self):
        cmds = [run_initialize(), gun_particle("gamma"), run_beam_on(10)]
        content = build_macro(cmds, comments=["Test macro"])
        assert content.startswith("# Test macro\n")
        assert "/run/initialize" in content
        assert "/gun/particle gamma" in content
        assert "/run/beamOn 10" in content

    def test_write_macro(self, tmp_path):
        path = str(tmp_path / "test.mac")
        cmds = [run_initialize(), gun_particle("proton"), run_beam_on(5)]
        result = write_macro(path, cmds)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "/run/initialize" in content
        assert "/gun/particle proton" in content


# ---------------------------------------------------------------------------
# Session tests
# ---------------------------------------------------------------------------

class TestSession:
    def test_create_default(self):
        s = Session()
        assert s.name == "sim"
        assert s.source["particle"] == "gamma"
        assert s.run["n_events"] == 1

    def test_create_named(self):
        s = Session(name="test_sim")
        assert s.name == "test_sim"

    def test_set_particle(self):
        s = Session()
        result = s.set_particle("proton")
        assert result == {"particle": "proton"}
        assert s.source["particle"] == "proton"

    def test_set_energy(self):
        s = Session()
        result = s.set_energy(210, "MeV")
        assert result == {"energy": 210, "unit": "MeV"}

    def test_set_direction(self):
        s = Session()
        result = s.set_direction(1, 0, 0)
        assert result == {"direction": [1, 0, 0]}

    def test_set_n_events(self):
        s = Session()
        result = s.set_n_events(10000)
        assert result == {"n_events": 10000}

    def test_set_cut(self):
        s = Session()
        result = s.set_cut(1.0, "mm")
        assert result == {"cut": 1.0, "unit": "mm"}

    def test_set_physics_list(self):
        s = Session()
        result = s.set_physics_list("FTFP_BERT")
        assert result == {"physics_list": "FTFP_BERT"}

    def test_set_magnetic_field(self):
        s = Session()
        result = s.set_magnetic_field(0, 0, 3.0, "tesla")
        assert result["bz"] == 3.0
        assert s.magnetic_field is not None

    def test_remove_magnetic_field(self):
        s = Session()
        s.set_magnetic_field(0, 0, 1.0)
        result = s.remove_magnetic_field()
        assert result == {"magnetic_field": None}
        assert s.magnetic_field is None

    def test_set_random_seeds(self):
        s = Session()
        result = s.set_random_seeds(42, 123)
        assert result == {"seeds": [42, 123]}

    def test_add_scoring_mesh(self):
        s = Session()
        result = s.add_scoring_mesh("dose", "box",
                                     {"dx": 10, "dy": 10, "dz": 10, "unit": "cm"})
        assert result["name"] == "dose"
        assert len(s.scoring) == 1

    def test_list_scoring(self):
        s = Session()
        s.add_scoring_mesh("mesh1")
        s.add_scoring_mesh("mesh2")
        result = s.list_scoring()
        assert len(result) == 2

    def test_remove_scoring(self):
        s = Session()
        s.add_scoring_mesh("mesh1")
        s.add_scoring_mesh("mesh2")
        result = s.remove_scoring("mesh1")
        assert result["removed"] == 1
        assert len(s.scoring) == 1

    def test_set_source_mode_invalid(self):
        s = Session()
        with pytest.raises(ValueError, match="Invalid source mode"):
            s.set_source_mode("invalid")

    def test_set_source_mode_gps(self):
        s = Session()
        result = s.set_source_mode("gps")
        assert result == {"mode": "gps"}

    def test_to_macro_commands(self):
        s = Session()
        s.set_particle("proton")
        s.set_energy(210, "MeV")
        s.set_direction(0, 0, 1)
        s.set_n_events(100)
        cmds = s.to_macro_commands()
        assert "/run/initialize" in cmds
        assert "/gun/particle proton" in cmds
        assert "/gun/energy 210 MeV" in cmds
        assert "/run/beamOn 100" in cmds

    def test_to_macro(self):
        s = Session()
        content = s.to_macro()
        assert "/run/initialize" in content
        assert "/gun/particle gamma" in content

    def test_save_load(self, tmp_path):
        s = Session(name="test_save")
        s.set_particle("proton")
        s.set_energy(100, "MeV")
        path = str(tmp_path / "session.json")
        s.save(path)

        loaded = Session.load(path)
        assert loaded.name == "test_save"
        assert loaded.source["particle"] == "proton"
        assert loaded.source["energy"] == 100

    def test_status(self):
        s = Session(name="status_test")
        status = s.status()
        assert status["name"] == "status_test"
        assert status["scoring_count"] == 0
        assert status["magnetic_field"] is False

    def test_modified_flag(self):
        s = Session()
        assert not s.modified
        s.set_particle("proton")
        assert s.modified

    def test_to_dict_from_dict(self):
        s = Session(name="roundtrip")
        s.set_particle("e-")
        s.set_magnetic_field(1, 0, 0, "tesla")
        d = s.to_dict()
        s2 = Session.from_dict(d)
        assert s2.name == "roundtrip"
        assert s2.source["particle"] == "e-"
        assert s2.magnetic_field is not None


# ---------------------------------------------------------------------------
# Backend tests (no Geant4 required — just checks discovery logic)
# ---------------------------------------------------------------------------

class TestBackend:
    def test_check_installation(self):
        from cli_anything.geant4.utils.geant4_backend import check_installation
        result = check_installation()
        assert "installed" in result
        # On a machine without Geant4, installed will be False
        assert isinstance(result["installed"], bool)

    def test_find_geant4_raises_without_install(self):
        from cli_anything.geant4.utils.geant4_backend import find_geant4_executable
        # Without GEANT4_EXECUTABLE set and no examples on PATH,
        # this should raise RuntimeError
        old = os.environ.pop("GEANT4_EXECUTABLE", None)
        try:
            with pytest.raises(RuntimeError, match="Geant4 executable not found"):
                find_geant4_executable()
        finally:
            if old:
                os.environ["GEANT4_EXECUTABLE"] = old

    def test_find_geant4_with_env_var(self, tmp_path):
        from cli_anything.geant4.utils.geant4_backend import find_geant4_executable
        fake_exe = str(tmp_path / "exampleB1")
        with open(fake_exe, "w") as f:
            f.write("#!/bin/sh\n")
        old = os.environ.get("GEANT4_EXECUTABLE")
        os.environ["GEANT4_EXECUTABLE"] = fake_exe
        try:
            result = find_geant4_executable()
            assert result == fake_exe
        finally:
            if old:
                os.environ["GEANT4_EXECUTABLE"] = old
            else:
                os.environ.pop("GEANT4_EXECUTABLE", None)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestCLI:
    def test_help(self):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Geant4" in result.output

    def test_version(self):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_check_command(self):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["check"])
        assert result.exit_code == 0

    def test_session_new(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        sf = str(tmp_path / "session.json")
        result = runner.invoke(cli, ["session", "new", "--name", "test", "-o", sf])
        assert result.exit_code == 0
        assert os.path.exists(sf)

    def test_source_set(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        sf = str(tmp_path / "session.json")
        runner.invoke(cli, ["session", "new", "-o", sf])
        result = runner.invoke(cli, ["-s", sf, "source", "set",
                                      "-p", "proton", "-e", "210",
                                      "--energy-unit", "MeV"])
        assert result.exit_code == 0

    def test_macro_generate(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        sf = str(tmp_path / "session.json")
        runner.invoke(cli, ["session", "new", "-o", sf])
        runner.invoke(cli, ["-s", sf, "source", "set", "-p", "gamma"])
        macro_path = str(tmp_path / "run.mac")
        result = runner.invoke(cli, ["-s", sf, "macro", "generate",
                                      "-o", macro_path])
        assert result.exit_code == 0
        assert os.path.exists(macro_path)
        with open(macro_path) as f:
            content = f.read()
        assert "/run/initialize" in content
        assert "/gun/particle gamma" in content

    def test_json_output(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "check"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "installed" in data

    def test_macro_validate(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        mac = str(tmp_path / "test.mac")
        with open(mac, "w") as f:
            f.write("/run/initialize\n/gun/particle gamma\n# comment\n")
        result = runner.invoke(cli, ["--json", "macro", "validate", mac])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is True

    def test_macro_validate_invalid(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.geant4.geant4_cli import cli
        runner = CliRunner()
        mac = str(tmp_path / "bad.mac")
        with open(mac, "w") as f:
            f.write("invalid_command\n")
        result = runner.invoke(cli, ["--json", "macro", "validate", mac])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is False
