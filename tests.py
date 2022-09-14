#!/usr/bin/env python3
"""Tests for schema which runs validation using schema over examples folder."""
# pylint: disable=redefined-outer-name

import json
from pathlib import Path

import jsonschema
import pytest
from ruamel.yaml import YAML

yaml = YAML(typ="safe")

root = Path(__file__).resolve().parent
examples_dir = root / "examples"
valid_dir = examples_dir / "valid"
invalid_dir = examples_dir / "invalid"


@pytest.fixture
def schema():
    return json.loads((root / "schema.json").read_text(encoding="utf-8"))


def ids_gen(val: str) -> str:
    if not isinstance(val, Path):
        return str(val)
    if val.name.endswith(".dvc.yaml"):
        return val.name[:-9]
    return val.name


@pytest.mark.parametrize("example", valid_dir.iterdir(), ids=ids_gen)
def test_valid_examples(schema, example):
    jsonschema.validate(yaml.load(example), schema=schema)


@pytest.mark.parametrize("example", invalid_dir.iterdir(), ids=ids_gen)
def test_invalid_examples(schema, example):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(yaml.load(example), schema=schema)
