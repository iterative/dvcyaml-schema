#!/usr/bin/env python
"""Tests for schema.

There are two tests here. One runs validation using schema over examples folder
and, other one uses `hypothesis` to generate random data to see if the
generated data fails to create a `dvc` stage.
"""
import json
import os
from copy import deepcopy
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

import hypothesis
import hypothesis_jsonschema
import jsonschema
from hypothesis import HealthCheck, Verbosity, given, settings

from dvc.repo import Repo
from dvc.utils.yaml import dump_yaml, load_yaml

schema = json.loads(Path("schema.json").read_text())
validate_schema = partial(jsonschema.validate, schema=schema)


# not to overcomplicate property-testing
modified_schema = deepcopy(schema)
stageProps = modified_schema["properties"]["stages"]["patternProperties"]
stagePropKey = list(stageProps.keys())[0]
stageProps["[A-Za-z0-9_-]+$"] = stageProps.pop(stagePropKey, {})

# Different profiles for CI, dev and debug, set it via `HYPOTHESIS_DEFAULT` env
common_kw = {
    "suppress_health_check": (
        HealthCheck.too_slow,
        HealthCheck.filter_too_much,
    )
}
settings.register_profile(
    "ci", max_examples=1000, print_blob=True, **common_kw
)
settings.register_profile("dev", max_examples=10, **common_kw)
settings.register_profile(
    "debug", max_examples=10, verbosity=Verbosity.verbose, **common_kw
)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "debug"))


def test_examples():
    """Validate schema over examples."""
    examples_dir = Path("examples")
    assert list(examples_dir.iterdir())

    for example in examples_dir.iterdir():
        try:
            validate_schema(load_yaml(example))
        except Exception:
            print("Failed to validate:", example)
            raise
        print("Validated", example)


@given(hypothesis_jsonschema.from_schema(modified_schema))
def test_load(repo, data):
    """See if data can create stage successfully."""
    # sanity test
    validate_schema(data)
    dump_yaml("dvc.yaml", data)
    repo._reset()
    stages = repo.stages
    if data.get("stages"):
        assert stages
    hypothesis.note(f"Stages: {stages}")


if __name__ == "__main__":
    test_examples()
    with TemporaryDirectory() as dir:
        os.chdir(dir)
        repo = Repo.init(no_scm=True)
        print("\nTesting with hypothesis in repo:", repo)
        test_load(repo)
