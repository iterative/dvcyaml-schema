#!/usr/bin/env python3
"""Tests for schema which runs validation using schema over examples folder."""

import json
from functools import partial
from pathlib import Path

import jsonschema
import pytest
from dvc.utils.serialize import load_yaml

schema = json.loads(
    (Path(__file__) / ".." / "schema.json").resolve().read_text()
)
validate_schema = partial(jsonschema.validate, schema=schema)

VALID_DIR = (Path(__file__) / ".." / "examples" / "valid").resolve()
INVALID_DIR = (Path(__file__) / ".." / "examples" / "invalid").resolve()


@pytest.mark.parametrize("example", 
    map(str, VALID_DIR.iterdir())
)
def test_valid_examples(example):
    validate_schema(load_yaml(example))


@pytest.mark.parametrize("example", 
    map(str, INVALID_DIR.iterdir())
)
def test_invalid_examples(example):
    with pytest.raises(jsonschema.ValidationError):
        validate_schema(load_yaml(example))

