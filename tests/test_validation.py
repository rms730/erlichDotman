import sys
import time

import pytest

from engineering_cascade.validation import run_commands


def test_validator_executes_argv_in_requested_directory_without_shell(tmp_path):
    result = run_commands([[sys.executable, "-c", "import os,sys;print(os.getcwd());"
                           "print(sys.argv[1]);sys.exit(7)", "$(touch escaped); a b"]],
                          tmp_path)[0]
    assert result["status"] == "failed"
    assert result["returncode"] == 7
    assert str(tmp_path) in result["stdout"]
    assert "$(touch escaped); a b" in result["stdout"]
    assert not (tmp_path / "escaped").exists()
    assert result["duration_ms"] >= 0


def test_timeout_reports_actual_returncode_and_keeps_partial_output(tmp_path):
    result = run_commands([[sys.executable, "-u", "-c",
                            "import time;print('started');time.sleep(5)"]],
                          tmp_path, timeout_seconds=0.05)[0]
    assert result["status"] == "timeout"
    assert result["timed_out"] is True
    assert result["returncode"] is not None
    assert result["returncode"] != 0
    assert "started" in result["stdout"]
    assert result["duration_ms"] < 2000


def test_validator_bounds_output_and_continues_after_failure(tmp_path):
    results = run_commands([
        [sys.executable, "-c", "import sys;print('a'*100000);sys.exit(1)"],
        [sys.executable, "-c", "print('ok')"],
    ], tmp_path)
    assert results[0]["output_truncated"] is True
    assert len(results[0]["stdout"]) <= 8192
    assert results[1]["status"] == "passed"
    assert results[1]["returncode"] == 0


def test_noisy_validator_has_bounded_capture_and_timeout(tmp_path):
    result = run_commands([[sys.executable, "-u", "-c",
                            "import os\nwhile True: os.write(1, b'x' * 8192)"]],
                          tmp_path, timeout_seconds=0.05)[0]
    assert result["status"] == "timeout"
    assert result["output_truncated"] is True
    assert len(result["stdout"]) <= 8192
    assert result["duration_ms"] < 2000


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX process-group cleanup")
def test_validator_cleans_up_background_children_when_leader_exits(tmp_path):
    child = "import time;from pathlib import Path;time.sleep(.2);Path('leaked').touch()"
    script = "import subprocess,sys;subprocess.Popen([sys.executable,'-c',sys.argv[1]])"
    result = run_commands([[sys.executable, "-c", script, child]], tmp_path)[0]
    assert result["returncode"] == 0
    time.sleep(0.3)
    assert not (tmp_path / "leaked").exists()


def test_missing_executable_is_error_with_unknown_returncode(tmp_path):
    result = run_commands([[str(tmp_path / "absent")]], tmp_path)[0]
    assert result["status"] == "error"
    assert result["returncode"] is None
    assert result["error"]


@pytest.mark.parametrize("commands", ["echo hi", ["echo hi"], [[]], [["echo", ""]],
                                      [[42]], [["echo\x00"]]])
def test_rejects_malformed_commands_before_executing(commands, tmp_path):
    with pytest.raises(ValueError):
        run_commands(commands, tmp_path)


@pytest.mark.parametrize("timeout", [0, -1, True, float("inf"), float("nan")])
def test_rejects_invalid_timeout(timeout, tmp_path):
    with pytest.raises(ValueError):
        run_commands([], tmp_path, timeout)
