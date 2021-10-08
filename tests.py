#!/usr/bin/env python3
"""Tests for schema which runs validation using schema over examples folder."""

import json
from functools import partial
from pathlib import Path

import jsonschema
from dvc.utils.serialize import load_yaml

schema = json.loads(
    (Path(__file__) / ".." / "schema.json").resolve().read_text()
)
validate_schema = partial(jsonschema.validate, schema=schema)


def test_examples():
    """Validate schema over examples."""
    examples_dir = (Path(__file__) / ".." / "examples").resolve()
    assert list(examples_dir.iterdir())

    for example in examples_dir.iterdir():
        try:
            validate_schema(load_yaml(example))
        except Exception:
            print("Failed to validate:", example)
            raise
        print("Validated", example)


if __name__ == "__main__":
    test_examples()
