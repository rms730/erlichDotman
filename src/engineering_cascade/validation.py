"""Bounded argv validation. Callers own execution permission and OS isolation."""

import math
import os
import signal
import subprocess
import threading
import time
from pathlib import Path

OUTPUT_LIMIT_BYTES = 8192


def _capture(stream, state):
    """Drain a pipe while retaining only a bounded prefix, without disk spooling."""
    try:
        while chunk := os.read(stream.fileno(), OUTPUT_LIMIT_BYTES):
            remaining = OUTPUT_LIMIT_BYTES - len(state["data"])
            state["data"].extend(chunk[:remaining])
            state["truncated"] |= len(chunk) > remaining
    except OSError:
        # Closing a timed-out validator's pipe may interrupt a platform pipe reader.
        pass


def _stop_group(process):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()


def run_commands(commands, cwd, timeout_seconds=10):
    """Run authorized argv lists sequentially, including gates after a failed gate.

    Output pipes are drained with bounded in-memory prefixes; output is never
    spooled to disk. This is a working directory, not a security sandbox. POSIX
    process groups are stopped after completion or timeout, including descendants.
    """
    if (isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds) or timeout_seconds <= 0):
        raise ValueError("timeout_seconds must be a positive finite number")
    if not isinstance(commands, list) or any(
        not isinstance(command, list) or not command or any(
            not isinstance(arg, str) or not arg or "\x00" in arg for arg in command
        ) for command in commands
    ):
        raise ValueError("Commands must be nonempty argv lists of nonempty strings")
    directory = Path(cwd).resolve()
    if not directory.is_dir():
        raise ValueError("Validation working directory does not exist")
    results = []
    for command in commands:
        started = time.monotonic()
        result = {"command": list(command), "returncode": None, "timed_out": False,
                  "status": "error", "error": None}
        states = [{"data": bytearray(), "truncated": False} for _ in range(2)]
        try:
            # The caller explicitly authorizes argv execution; shell expansion is disabled.
            with subprocess.Popen(  # noqa: S603
                command, cwd=directory, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
                shell=False, start_new_session=os.name == "posix",
            ) as process:
                readers = [threading.Thread(target=_capture, args=(stream, state), daemon=True)
                           for stream, state in zip((process.stdout, process.stderr), states,
                                                    strict=True)]
                for reader in readers:
                    reader.start()
                try:
                    process.wait(timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    result["timed_out"] = True
                finally:
                    _stop_group(process)
                    process.wait()
                    for reader in readers:
                        reader.join(timeout=0.5)
                result["returncode"] = process.returncode
                result["status"] = ("timeout" if result["timed_out"] else
                                    "passed" if process.returncode == 0 else "failed")
        except OSError as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
        result["duration_ms"] = (time.monotonic() - started) * 1000
        result["stdout"], result["stderr"] = (
            bytes(state["data"]).decode("utf-8", errors="replace") for state in states
        )
        result["output_truncated"] = any(state["truncated"] for state in states)
        results.append(result)
    return results
