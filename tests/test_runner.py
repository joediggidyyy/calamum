"""Tests for calamum.runner — streaming supervision, heartbeat cadence, and hardening paths.

Coverage targets (per Phase 5 plan):
- _supervise_step: stdout/stderr captured to files and returned as text
- _supervise_step: heartbeat emitted at configured interval
- _supervise_step: heartbeat NOT emitted for fast steps (interval not reached)
- _supervise_step: non-zero return code propagated correctly
- run_step: result classification (pass / failed / allowed_failure / planned)
- run_step: env_keys filtered to CALAMUM_ prefix
- run_step: heartbeat fields excluded from returned step packet
- HEARTBEAT_INTERVAL_SEC: constant is 20
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from calamum import runner
from calamum.runner import (
    HEARTBEAT_INTERVAL_SEC,
    _supervise_step,
    run_step,
)


# ---------------------------------------------------------------------------
# _supervise_step
# ---------------------------------------------------------------------------

class TestSuperviseStep:
    def test_captures_stdout_to_file_and_return(self, tmp_path):
        stdout_path = tmp_path / "step.stdout.txt"
        stderr_path = tmp_path / "step.stderr.txt"

        returncode, stdout_text, stderr_text = _supervise_step(
            command=[sys.executable, "-c", "print('hello stdout')"],
            cwd=tmp_path,
            env=dict(os.environ),
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            shell=False,
            run_id="test-run",
            lane="pytest",
            step_id="test-step",
        )

        assert returncode == 0
        assert "hello stdout" in stdout_text
        assert "hello stdout" in stdout_path.read_text(encoding="utf-8")

    def test_captures_stderr_to_file_and_return(self, tmp_path):
        stdout_path = tmp_path / "step.stdout.txt"
        stderr_path = tmp_path / "step.stderr.txt"

        returncode, stdout_text, stderr_text = _supervise_step(
            command=[sys.executable, "-c", "import sys; print('hello stderr', file=sys.stderr)"],
            cwd=tmp_path,
            env=dict(os.environ),
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            shell=False,
            run_id="test-run",
            lane="pytest",
            step_id="test-step",
        )

        assert returncode == 0
        assert "hello stderr" in stderr_text
        assert "hello stderr" in stderr_path.read_text(encoding="utf-8")

    def test_nonzero_returncode_propagated(self, tmp_path):
        stdout_path = tmp_path / "step.stdout.txt"
        stderr_path = tmp_path / "step.stderr.txt"

        returncode, _, _ = _supervise_step(
            command=[sys.executable, "-c", "raise SystemExit(7)"],
            cwd=tmp_path,
            env=dict(os.environ),
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            shell=False,
            run_id="r",
            lane="l",
            step_id="s",
        )

        assert returncode == 7

    def test_heartbeat_emitted_at_interval(self, tmp_path):
        emitted = []

        def capture(msg):
            emitted.append(msg)

        stdout_path = tmp_path / "step.stdout.txt"
        stderr_path = tmp_path / "step.stderr.txt"

        with patch.object(runner, "_emit_heartbeat", side_effect=capture):
            _supervise_step(
                command=[sys.executable, "-c", "import time; time.sleep(0.7)"],
                cwd=tmp_path,
                env=dict(os.environ),
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                shell=False,
                run_id="hb-run",
                lane="pytest",
                step_id="sleep-step",
                heartbeat_interval=0.2,
            )

        assert len(emitted) >= 1
        assert all("[calamum heartbeat]" in m for m in emitted)
        assert all("hb-run" in m for m in emitted)
        assert all("sleep-step" in m for m in emitted)
        assert all("pytest" in m for m in emitted)

    def test_heartbeat_not_emitted_when_step_is_fast(self, tmp_path):
        emitted = []

        def capture(msg):
            emitted.append(msg)

        stdout_path = tmp_path / "step.stdout.txt"
        stderr_path = tmp_path / "step.stderr.txt"

        with patch.object(runner, "_emit_heartbeat", side_effect=capture):
            _supervise_step(
                command=[sys.executable, "-c", "print('fast')"],
                cwd=tmp_path,
                env=dict(os.environ),
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                shell=False,
                run_id="fast-run",
                lane="pytest",
                step_id="fast-step",
                heartbeat_interval=30,
            )

        assert len(emitted) == 0

    def test_heartbeat_payload_excludes_env_values(self, tmp_path):
        """Heartbeat lines must not contain env values — only safe progress fields."""
        emitted = []

        def capture(msg):
            emitted.append(msg)

        stdout_path = tmp_path / "step.stdout.txt"
        stderr_path = tmp_path / "step.stderr.txt"

        with patch.object(runner, "_emit_heartbeat", side_effect=capture):
            _supervise_step(
                command=[sys.executable, "-c", "import time; time.sleep(0.7)"],
                cwd=tmp_path,
                env={"PATH": "/usr/bin", "CALAMUM_SECRET_KEY": "supersecret"},
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                shell=False,
                run_id="r",
                lane="pytest",
                step_id="s",
                heartbeat_interval=0.2,
            )

        for msg in emitted:
            assert "supersecret" not in msg
            assert "CALAMUM_SECRET_KEY" not in msg


# ---------------------------------------------------------------------------
# run_step result classification
# ---------------------------------------------------------------------------

class TestRunStepResultClassification:
    def test_pass_result(self, tmp_path):
        step = {
            "id": "s-pass",
            "title": "Pass step",
            "command": [sys.executable, "-c", "print('ok')"],
        }
        result = run_step(step, tmp_path, dry_run=False)
        assert result["result"] == "pass"
        assert result["returncode"] == 0

    def test_failed_result(self, tmp_path):
        step = {
            "id": "s-fail",
            "title": "Fail step",
            "command": [sys.executable, "-c", "raise SystemExit(1)"],
        }
        result = run_step(step, tmp_path, dry_run=False)
        assert result["result"] == "failed"
        assert result["returncode"] == 1

    def test_allowed_failure(self, tmp_path):
        step = {
            "id": "s-allowed",
            "title": "Allowed failure",
            "command": [sys.executable, "-c", "raise SystemExit(2)"],
            "allow_failure": True,
        }
        result = run_step(step, tmp_path, dry_run=False)
        assert result["result"] == "allowed_failure"
        assert result["returncode"] == 2

    def test_dry_run_returns_planned(self, tmp_path):
        step = {
            "id": "s-dry",
            "title": "Dry run step",
            "command": [sys.executable, "-c", "print('should not run')"],
        }
        result = run_step(step, tmp_path, dry_run=True)
        assert result["result"] == "planned"
        assert result["returncode"] is None


# ---------------------------------------------------------------------------
# run_step env_keys contract
# ---------------------------------------------------------------------------

class TestRunStepEnvKeys:
    def test_env_keys_filtered_to_calamum_prefix(self, tmp_path):
        step = {
            "id": "s-env",
            "title": "Env step",
            "command": [sys.executable, "-c", "print('ok')"],
            "env": {"CALAMUM_MY_KEY": "v1", "UNRELATED_VAR": "v2"},
        }
        result = run_step(step, tmp_path, dry_run=False)
        assert "CALAMUM_MY_KEY" in result["env_keys"]
        assert "UNRELATED_VAR" not in result["env_keys"]

    def test_env_values_absent_from_step_result(self, tmp_path):
        step = {
            "id": "s-env2",
            "title": "Env values absent",
            "command": [sys.executable, "-c", "print('ok')"],
            "env": {"CALAMUM_TOKEN": "topsecret"},
        }
        result = run_step(step, tmp_path, dry_run=False)
        result_str = str(result)
        assert "topsecret" not in result_str


# ---------------------------------------------------------------------------
# run_step heartbeat fields excluded from returned packet
# ---------------------------------------------------------------------------

class TestRunStepPacketShape:
    def test_heartbeat_fields_not_in_result_packet(self, tmp_path):
        """Heartbeat emission must not pollute the step result dict."""
        step = {
            "id": "s-hb",
            "title": "Heartbeat packet shape",
            "command": [sys.executable, "-c", "import time; time.sleep(0.4)"],
        }
        result = run_step(step, tmp_path, dry_run=False, _run_id="r", _lane="l")
        assert "heartbeat" not in result
        assert "elapsed_sec" not in result
        assert "interval_sec" not in result

    def test_result_packet_has_required_fields(self, tmp_path):
        step = {
            "id": "s-fields",
            "title": "Field check",
            "command": [sys.executable, "-c", "print('ok')"],
        }
        result = run_step(step, tmp_path, dry_run=False)
        required = {"id", "title", "command_display", "result", "returncode",
                    "cwd", "env_keys", "expected_artifacts", "evidence_requirements",
                    "notes", "stdout_path", "stderr_path"}
        assert required.issubset(result.keys())


# ---------------------------------------------------------------------------
# HEARTBEAT_INTERVAL_SEC constant
# ---------------------------------------------------------------------------

class TestHeartbeatConstant:
    def test_default_interval_is_20(self):
        assert HEARTBEAT_INTERVAL_SEC == 20


# ===========================================================================
# ADVERSARIAL + EDGE-CASE TESTS
# ===========================================================================

import json as _json
import re as _re

from calamum.runner import (
    RunError,
    _drain_pipe,
    run_definition,
    run_lane,
)


# ---------------------------------------------------------------------------
# Heartbeat format parsability
# ---------------------------------------------------------------------------

class TestHeartbeatFormat:
    """Assert that every heartbeat line contains all required fields in parsable form."""

    def _collect_heartbeats(self, tmp_path, duration: float = 0.7, interval: float = 0.2) -> list:
        emitted = []
        stdout_path = tmp_path / "hb.stdout.txt"
        stderr_path = tmp_path / "hb.stderr.txt"
        with patch.object(runner, "_emit_heartbeat", side_effect=emitted.append):
            _supervise_step(
                command=[sys.executable, "-c",
                         "import time; time.sleep({0})".format(duration)],
                cwd=tmp_path,
                env=dict(os.environ),
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                shell=False,
                run_id="fmt-run",
                lane="pytest",
                step_id="fmt-step",
                heartbeat_interval=interval,
            )
        return emitted

    def test_heartbeat_contains_all_required_keys(self, tmp_path):
        msgs = self._collect_heartbeats(tmp_path)
        assert msgs, "Expected at least one heartbeat"
        for msg in msgs:
            assert "run=" in msg
            assert "lane=" in msg
            assert "step=" in msg
            assert "elapsed=" in msg
            assert "interval=" in msg
            assert "cwd=" in msg

    def test_heartbeat_elapsed_is_numeric(self, tmp_path):
        msgs = self._collect_heartbeats(tmp_path)
        for msg in msgs:
            m = _re.search(r"elapsed=(\d+)s", msg)
            assert m, "elapsed field missing or non-numeric in: {0}".format(msg)
            assert int(m.group(1)) >= 0

    def test_heartbeat_interval_field_present_and_numeric(self, tmp_path):
        msgs = self._collect_heartbeats(tmp_path, interval=0.2)
        for msg in msgs:
            m = _re.search(r"interval=([0-9.]+)s", msg)
            assert m, "interval field missing in: {0}".format(msg)
            assert float(m.group(1)) >= 0

    def test_heartbeat_contains_run_id_value(self, tmp_path):
        msgs = self._collect_heartbeats(tmp_path)
        assert all("fmt-run" in m for m in msgs)

    def test_heartbeat_contains_step_id_value(self, tmp_path):
        msgs = self._collect_heartbeats(tmp_path)
        assert all("fmt-step" in m for m in msgs)

    def test_heartbeat_contains_lane_value(self, tmp_path):
        msgs = self._collect_heartbeats(tmp_path)
        assert all("pytest" in m for m in msgs)

    def test_multiple_heartbeats_have_nondecreasing_elapsed(self, tmp_path):
        msgs = self._collect_heartbeats(tmp_path, duration=1.5, interval=0.2)
        if len(msgs) < 2:
            pytest.skip("Need at least 2 heartbeats for ordering check")
        elapsed_values = []
        for msg in msgs:
            m = _re.search(r"elapsed=(\d+)s", msg)
            if m:
                elapsed_values.append(int(m.group(1)))
        for i in range(1, len(elapsed_values)):
            assert elapsed_values[i] >= elapsed_values[i - 1], (
                "Heartbeat elapsed went backwards: {0}".format(elapsed_values)
            )


# ---------------------------------------------------------------------------
# Hostile identifiers (log-injection hardening)
# ---------------------------------------------------------------------------

class TestHostileIdentifiers:
    """Confirm heartbeat behavior under hostile step_id / run_id values.
    run_id produced by build_run_id() is always safe; step_id comes from
    trusted catalog definitions. These tests probe the internal interface."""

    def test_newline_in_step_id_does_not_produce_second_heartbeat_prefix(self, tmp_path):
        emitted = []
        stdout_path = tmp_path / "hb.stdout.txt"
        stderr_path = tmp_path / "hb.stderr.txt"
        with patch.object(runner, "_emit_heartbeat", side_effect=emitted.append):
            _supervise_step(
                command=[sys.executable, "-c", "import time; time.sleep(0.5)"],
                cwd=tmp_path,
                env=dict(os.environ),
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                shell=False,
                run_id="run-safe",
                lane="pytest",
                step_id="step\nINJECTED",
                heartbeat_interval=0.1,
            )
        for msg in emitted:
            lines = msg.split("\n")
            hb_line_count = sum(1 for ln in lines if "[calamum heartbeat]" in ln)
            assert hb_line_count <= 1, (
                "Heartbeat message should not produce multiple header prefixes; got: {0!r}".format(msg)
            )

    def test_path_separator_in_run_id_first_heartbeat_line_has_prefix(self, tmp_path):
        emitted = []
        stdout_path = tmp_path / "hb.stdout.txt"
        stderr_path = tmp_path / "hb.stderr.txt"
        with patch.object(runner, "_emit_heartbeat", side_effect=emitted.append):
            _supervise_step(
                command=[sys.executable, "-c", "import time; time.sleep(0.5)"],
                cwd=tmp_path,
                env=dict(os.environ),
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                shell=False,
                run_id="../../../probe",
                lane="pytest",
                step_id="s",
                heartbeat_interval=0.1,
            )
        for msg in emitted:
            first_line = msg.split("\n")[0]
            assert first_line.startswith("[calamum heartbeat]")

    def test_process_stdout_secret_absent_from_heartbeat(self, tmp_path):
        """Subprocess printing a secret to stdout must not appear in heartbeat."""
        emitted = []
        stdout_path = tmp_path / "hb.stdout.txt"
        stderr_path = tmp_path / "hb.stderr.txt"
        with patch.object(runner, "_emit_heartbeat", side_effect=emitted.append):
            _supervise_step(
                command=[sys.executable, "-c",
                         "import time; print('CALAMUM_SECRET=abc123'); time.sleep(0.5)"],
                cwd=tmp_path,
                env=dict(os.environ),
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                shell=False,
                run_id="r",
                lane="pytest",
                step_id="s",
                heartbeat_interval=0.1,
            )
        for msg in emitted:
            assert "abc123" not in msg
            assert "CALAMUM_SECRET" not in msg
        # The secret MUST appear in the captured stdout file
        assert "abc123" in stdout_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Large and unicode output
# ---------------------------------------------------------------------------

class TestLargeAndUnicodeOutput:
    def test_large_stdout_fully_captured(self, tmp_path):
        """500 lines of stdout must be fully present in file and return value."""
        stdout_path = tmp_path / "large.stdout.txt"
        stderr_path = tmp_path / "large.stderr.txt"
        script = "for i in range(500):\n    print('line-{0}'.format(i))\n"
        returncode, stdout_text, _ = _supervise_step(
            command=[sys.executable, "-c", script],
            cwd=tmp_path,
            env=dict(os.environ),
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            shell=False,
            run_id="r",
            lane="pytest",
            step_id="s",
        )
        assert returncode == 0
        for i in (0, 250, 499):
            assert "line-{0}".format(i) in stdout_text
            assert "line-{0}".format(i) in stdout_path.read_text(encoding="utf-8")

    def test_unicode_stdout_captured_without_crash(self, tmp_path):
        stdout_path = tmp_path / "unicode.stdout.txt"
        stderr_path = tmp_path / "unicode.stderr.txt"
        # PYTHONUTF8=1 ensures the child subprocess uses UTF-8 stdout regardless
        # of the Windows console code page. This is the correct probe for non-ASCII
        # streaming capture.
        utf8_env = dict(os.environ)
        utf8_env["PYTHONUTF8"] = "1"
        returncode, stdout_text, _ = _supervise_step(
            command=[sys.executable, "-c",
                     "print('caf\\u00e9 \\u4e2d\\u6587 \\u00e9l\\u00e8ve')"],
            cwd=tmp_path,
            env=utf8_env,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            shell=False,
            run_id="r",
            lane="pytest",
            step_id="s",
        )
        assert returncode == 0
        # café prefix must survive round-trip through streaming drain + UTF-8 decode
        assert "caf" in stdout_text

    def test_empty_stdout_creates_files(self, tmp_path):
        stdout_path = tmp_path / "empty.stdout.txt"
        stderr_path = tmp_path / "empty.stderr.txt"
        returncode, stdout_text, stderr_text = _supervise_step(
            command=[sys.executable, "-c", ""],
            cwd=tmp_path,
            env=dict(os.environ),
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            shell=False,
            run_id="r",
            lane="pytest",
            step_id="s",
        )
        assert returncode == 0
        assert stdout_path.exists()
        assert stderr_path.exists()

    def test_simultaneous_stdout_and_stderr(self, tmp_path):
        stdout_path = tmp_path / "both.stdout.txt"
        stderr_path = tmp_path / "both.stderr.txt"
        script = (
            "import sys\n"
            "for i in range(50):\n"
            "    sys.stdout.write('out-{0}\\n'.format(i))\n"
            "    sys.stderr.write('err-{0}\\n'.format(i))\n"
            "sys.stdout.flush()\n"
            "sys.stderr.flush()\n"
        )
        returncode, stdout_text, stderr_text = _supervise_step(
            command=[sys.executable, "-c", script],
            cwd=tmp_path,
            env=dict(os.environ),
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            shell=False,
            run_id="r",
            lane="pytest",
            step_id="s",
        )
        assert returncode == 0
        assert "out-0" in stdout_text and "out-49" in stdout_text
        assert "err-0" in stderr_text and "err-49" in stderr_text


# ---------------------------------------------------------------------------
# Subprocess hardening: exotic exit codes + stderr-on-failure
# ---------------------------------------------------------------------------

class TestSubprocessHardening:
    def test_exit_code_127_classified_failed(self, tmp_path):
        step = {"id": "s", "title": "T", "command": [sys.executable, "-c", "raise SystemExit(127)"]}
        result = run_step(step, tmp_path, dry_run=False)
        assert result["result"] == "failed"
        assert result["returncode"] == 127

    def test_exit_code_255_classified_failed(self, tmp_path):
        step = {"id": "s", "title": "T", "command": [sys.executable, "-c", "raise SystemExit(255)"]}
        result = run_step(step, tmp_path, dry_run=False)
        assert result["result"] == "failed"
        assert result["returncode"] == 255

    def test_exit_code_255_with_allow_failure(self, tmp_path):
        step = {"id": "s", "title": "T",
                "command": [sys.executable, "-c", "raise SystemExit(255)"],
                "allow_failure": True}
        result = run_step(step, tmp_path, dry_run=False)
        assert result["result"] == "allowed_failure"

    def test_stderr_on_failure_captured_to_file(self, tmp_path):
        step = {
            "id": "s-err", "title": "T",
            "command": [sys.executable, "-c",
                        "import sys; sys.stderr.write('failure detail\\n'); raise SystemExit(1)"],
        }
        result = run_step(step, tmp_path, dry_run=False)
        assert result["result"] == "failed"
        assert "failure detail" in Path(result["stderr_path"]).read_text(encoding="utf-8")

    def test_stdout_and_stderr_paths_within_lane_dir(self, tmp_path):
        step = {"id": "containment-step", "title": "T",
                "command": [sys.executable, "-c", "print('ok')"]}
        result = run_step(step, tmp_path, dry_run=False)
        assert Path(result["stdout_path"]).parent == tmp_path
        assert Path(result["stderr_path"]).parent == tmp_path


# ---------------------------------------------------------------------------
# Lane orchestration: multi-step failure propagation
# ---------------------------------------------------------------------------

class TestLaneOrchestration:
    def test_multi_step_first_fails_second_still_executes(self, tmp_path):
        """All steps execute even after first failure; lane result = 'failed'."""
        steps = [
            {"id": "s1", "title": "Fail",
             "command": [sys.executable, "-c", "raise SystemExit(1)"]},
            {"id": "s2", "title": "Pass",
             "command": [sys.executable, "-c", "print('second ok')"]},
        ]
        lane_report = run_lane("pytest", steps, tmp_path / "pytest", dry_run=False)
        assert lane_report["result"] == "failed"
        assert lane_report["steps"][0]["result"] == "failed"
        assert lane_report["steps"][1]["result"] == "pass"

    def test_multi_step_all_pass(self, tmp_path):
        steps = [
            {"id": "s1", "title": "S1", "command": [sys.executable, "-c", "print('a')"]},
            {"id": "s2", "title": "S2", "command": [sys.executable, "-c", "print('b')"]},
        ]
        lane_report = run_lane("pytest", steps, tmp_path / "pytest", dry_run=False)
        assert lane_report["result"] == "pass"
        assert all(s["result"] == "pass" for s in lane_report["steps"])

    def test_empty_lane_returns_not_applicable(self, tmp_path):
        lane_report = run_lane("pytest", [], tmp_path / "pytest", dry_run=False)
        assert lane_report["result"] == "not_applicable"
        assert lane_report["steps"] == []

    def test_allowed_failure_does_not_set_lane_to_failed(self, tmp_path):
        steps = [
            {"id": "s1", "title": "S1",
             "command": [sys.executable, "-c", "raise SystemExit(1)"],
             "allow_failure": True},
            {"id": "s2", "title": "S2",
             "command": [sys.executable, "-c", "print('ok')"]},
        ]
        lane_report = run_lane("pytest", steps, tmp_path / "pytest", dry_run=False)
        assert lane_report["result"] != "failed"
        assert lane_report["steps"][0]["result"] == "allowed_failure"


# ---------------------------------------------------------------------------
# run_definition: retained-artifact contract under failure
# ---------------------------------------------------------------------------

class TestRunDefinitionArtifactContract:
    """Retained artifacts must be written even when a step fails (no-go run)."""

    def _make_definition(self, step_command, allow_failure=False):
        return {
            "id": "artifact-contract-test",
            "title": "Artifact contract",
            "summary": "Test artifact writes under failure.",
            "status": "active",
            "category": "regression",
            "selector_policy": "exact-name-only",
            "profiles": ["default"],
            "tags": ["regression"],
            "policy_flags": ["json-first"],
            "evidence_requirements": ["report_json"],
            "default_lanes": ["pytest"],
            "lanes": {
                "pytest": [
                    {"id": "probe-step", "title": "Probe",
                     "command": step_command, "allow_failure": allow_failure}
                ]
            },
        }

    def _assert_artifacts_exist(self, report):
        for key in ("report_json", "report_md", "manifest_json", "checksums_json"):
            path = Path(report["artifacts"][key])
            assert path.exists(), "Artifact missing: {0}".format(key)

    def test_artifacts_written_on_passing_run(self, tmp_path):
        report = run_definition(self._make_definition([sys.executable, "-c", "print('ok')"]),
                                runs_root=tmp_path / "runs")
        self._assert_artifacts_exist(report)
        assert report["decision"] == "go"

    def test_artifacts_written_on_failing_run(self, tmp_path):
        report = run_definition(self._make_definition([sys.executable, "-c", "raise SystemExit(1)"]),
                                runs_root=tmp_path / "runs")
        self._assert_artifacts_exist(report)
        assert report["decision"] == "no-go"
        assert report["result"] == "failed"

    def test_run_index_appended_on_failing_run(self, tmp_path):
        run_definition(self._make_definition([sys.executable, "-c", "raise SystemExit(1)"]),
                       runs_root=tmp_path / "runs")
        index_path = tmp_path / "runs" / "run_index.jsonl"
        assert index_path.exists()
        rows = [_json.loads(l) for l in index_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(rows) == 1
        assert rows[0]["result"] == "failed"

    def test_checksum_sidecars_written_on_failing_run(self, tmp_path):
        report = run_definition(self._make_definition([sys.executable, "-c", "raise SystemExit(1)"]),
                                runs_root=tmp_path / "runs")
        for sidecar_path in report["artifacts"].get("checksum_sidecars", []):
            assert Path(sidecar_path).exists(), "Sidecar missing: {0}".format(sidecar_path)

    def test_run_id_in_report_matches_run_dir_name(self, tmp_path):
        report = run_definition(self._make_definition([sys.executable, "-c", "print('ok')"]),
                                runs_root=tmp_path / "runs")
        assert Path(report["run_dir"]).name == report["run_id"]


# ---------------------------------------------------------------------------
# run_definition: run_id format + disk consistency
# ---------------------------------------------------------------------------

class TestRunDefinitionRunIdIntegrity:
    def _make_definition(self):
        return {
            "id": "id-integrity-test",
            "title": "T", "summary": "S", "status": "active",
            "category": "regression", "selector_policy": "exact-name-only",
            "profiles": [], "tags": [], "policy_flags": [],
            "evidence_requirements": [],
            "default_lanes": ["pytest"],
            "lanes": {
                "pytest": [
                    {"id": "s", "title": "S",
                     "command": [sys.executable, "-c", "print('x')"]}
                ]
            },
        }

    def test_run_id_has_timestamp_slug_format(self, tmp_path):
        report = run_definition(self._make_definition(), runs_root=tmp_path / "runs")
        assert _re.match(r"^\d{8}T\d{6}Z-", report["run_id"]), (
            "run_id format unexpected: {0}".format(report["run_id"])
        )

    def test_report_json_on_disk_matches_returned_run_id(self, tmp_path):
        report = run_definition(self._make_definition(), runs_root=tmp_path / "runs")
        on_disk = _json.loads(
            Path(report["artifacts"]["report_json"]).read_text(encoding="utf-8")
        )
        assert on_disk["run_id"] == report["run_id"]

    def test_manifest_json_on_disk_has_correct_run_id(self, tmp_path):
        report = run_definition(self._make_definition(), runs_root=tmp_path / "runs")
        on_disk = _json.loads(
            Path(report["artifacts"]["manifest_json"]).read_text(encoding="utf-8")
        )
        assert on_disk["run_id"] == report["run_id"]
