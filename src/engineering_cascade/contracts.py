"""Validate versioned public contracts without loading remote schemas."""

import json
import math
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator

MAX_NESTING_DEPTH = 64


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _invalid_number(value):
    raise ValueError("Non-finite JSON number")


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite JSON number")
    return number


def load_json(path, max_bytes=4 * 1024 * 1024):
    """Read bounded, unambiguous UTF-8 JSON. Never execute content."""
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("Invalid JSON byte budget")
    with Path(path).open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError("JSON exceeds byte budget")
    try:
        document = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_number,
            parse_float=_finite_float,
        )
        _check_finite(document)
        return document
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("Invalid UTF-8 JSON") from exc


@lru_cache(maxsize=16)
def _validator(kind):
    schema = json.loads(files("engineering_cascade").joinpath(
        "schemas/contracts.schema.json"
    ).read_text(encoding="utf-8"))
    if kind not in schema["$defs"]:
        raise ValueError("Unknown contract")
    schema["$ref"] = f"#/$defs/{kind}"
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _check_finite(document, depth=0):
    if depth > MAX_NESTING_DEPTH:
        raise ValueError("JSON exceeds nesting limit")
    if isinstance(document, float) and not math.isfinite(document):
        raise ValueError("Non-finite contract value")
    if isinstance(document, dict):
        for value in document.values():
            _check_finite(value, depth + 1)
    elif isinstance(document, (list, tuple)):
        for value in document:
            _check_finite(value, depth + 1)


def validate(document, kind):
    """Raise ValueError on invalid input, without printing potentially private values."""
    try:
        _check_finite(document)
        error = next(_validator(kind).iter_errors(document), None)
    except RecursionError as exc:
        raise ValueError("Contract exceeds nesting limit") from exc
    if error is not None:
        path = ".".join(str(part) for part in error.absolute_path) or "root"
        raise ValueError(f"Invalid {kind} at {path}: {error.validator}")
