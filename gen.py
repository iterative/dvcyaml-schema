#!/usr/bin/env python3
"""schema.json generator."""
# import re
from typing import Any, NewType

from pydantic import BaseModel, ConfigDict, Field, RootModel

# aliases
FilePath = NewType("FilePath", str)
VarKey = NewType("VarKey", str)
StageName = NewType("StageName", str)
PlotIdOrFilePath = NewType("PlotIdOrFilePath", str)
PlotColumn = NewType("PlotColumn", str)
PlotColumns = str | set[PlotColumn]
PlotTemplateName = NewType("PlotTemplateName", str)


class OutFlags(BaseModel):
    cache: bool | None = Field(True, description="Cache output by DVC")
    persist: bool | None = Field(
        False, description="Persist output between runs"
    )
    checkpoint: bool | None = Field(
        False,
        description="Indicate that the output is associated with "
        "in-code checkpoints",
    )
    desc: str | None = Field(
        None,
        description="User description for the output",
        title="Description",
    )
    type: str | None = Field(
        None, description="User assigned type of the output", title="Type"
    )
    labels: set[str] | None = Field(
        default_factory=set,
        description="User assigned labels of the output",
        title="Labels",
    )
    meta: dict[str, Any] | None = Field(
        None, description="Custom metadata of the output.", title="Meta"
    )
    remote: str | None = Field(
        None, description="Name of the remote to use for pushing/fetching"
    )
    push: bool | None = Field(
        True,
        description="Whether the output should be pushed to remote "
        "during `dvc push`",
    )
    model_config = ConfigDict(extra="forbid")


class PlotFlags(OutFlags):
    x: PlotColumn = Field(
        None, description="Default field name to use as x-axis data"
    )
    y: PlotColumn = Field(
        None, description="Default field name to use as y-axis data"
    )
    x_label: str = Field(None, description="Default label for the x-axis")
    y_label: str = Field(None, description="Default label for the y-axis")
    title: str = Field(None, description="Default plot title")
    header: bool = Field(
        False, description="Whether the target CSV or TSV has a header or not"
    )
    template: FilePath = Field(None, description="Default plot template")


# pylint: disable=invalid-name
class X(RootModel):
    root: dict[FilePath, PlotColumn] = Field(default_factory=dict)


# pylint: disable=invalid-name
class Y(RootModel):
    root: dict[FilePath, PlotColumns] = Field(default_factory=dict)


class TopLevelPlotFlags(BaseModel):
    x: PlotColumn | X = Field(
        None,
        description=(
            "A single column name, "
            "or a dictionary of data-source and column pair"
        ),
    )
    y: PlotColumns | Y = Field(
        default_factory=dict,
        description=(
            "A single column name, list of columns,"
            " or a dictionary of data-source and column pair"
        ),
    )
    x_label: str = Field(None, description="Default label for the x-axis")
    y_label: str = Field(None, description="Default label for the y-axis")
    title: str = Field(None, description="Default plot title")
    template: str = Field(
        default="linear", description="Default plot template"
    )
    model_config = ConfigDict(extra="forbid")


class EmptyTopLevelPlotFlags(RootModel):
    root: None = None


class TopLevelArtifactFlags(BaseModel):
    path: str = Field(description="Path to the artifact")
    type: str = Field(None, description="Type of the artifact")
    desc: str = Field(None, description="Description for the artifact")
    meta: dict[str, Any] = Field(
        None, description="Custom metadata for the artifact"
    )
    labels: set[str] = Field(
        default_factory=set, description="Labels for the artifact"
    )
    model_config = ConfigDict(extra="forbid")


DEP_DESC = "Path to a dependency (input) file or directory for the stage."


class DepModel(RootModel):
    root: FilePath = Field(..., description=DEP_DESC)


class Dependencies(RootModel):
    root: set[DepModel]


class ParamKey(RootModel):
    root: str = Field(..., desc="Parameter name (dot-separated).")


class CustomParamFileKeys(RootModel):
    root: dict[FilePath, set[ParamKey]] = Field(
        ..., desc="Path to YAML/JSON/TOML/Python params file."
    )


class EmptyParamFileKeys(RootModel):
    root: dict[FilePath, None] = Field(
        ..., desc="Path to YAML/JSON/TOML/Python params file."
    )


class Param(RootModel):
    root: ParamKey | CustomParamFileKeys | EmptyParamFileKeys


class Params(RootModel):
    root: set[Param]


class Out(RootModel):
    root: FilePath | dict[FilePath, OutFlags] = Field(
        ..., description="Path to an output file or dir of the stage."
    )


class Outs(RootModel):
    root: set[Out]


class Metric(RootModel):
    root: FilePath | dict[FilePath, OutFlags] = Field(
        ...,
        description="Path to a JSON/TOML/YAML metrics output of the stage.",
    )


PLOT_DESC = """\
Path to plots file or dir of the stage.

Data files may be JSON/YAML/CSV/TSV.

Image files may be JPEG/GIF/PNG."""


class Plot(RootModel):
    root: FilePath | dict[FilePath, PlotFlags] = Field(
        ..., description=PLOT_DESC
    )


class Plots(RootModel):
    root: set[Plot]


class VarPath(RootModel):
    root: str = Field(
        ..., description="Path to params file with values for substitution."
    )


class VarDecl(RootModel):
    # {"foo" (str) : "foobar" (Any) }
    root: dict[VarKey, Any] = Field(
        ..., description="Dict of values for substitution."
    )


class Vars(RootModel):
    root: list[VarPath | VarDecl]


STAGE_VARS_DESC = """\
List of stage-specific values for substitution.

May include any dict or a path to a params file.

Use in the stage with the `${}` substitution expression."""

CMD_DESC = """\
(Required) Command to run (anything your system terminal can run).

Can be a string or a list of commands."""

PARAMS_DESC = """\
List of dot-separated parameter dependency keys to track from `params.yaml`.

May contain other YAML/JSON/TOML/Python parameter file names, with a \
sub-list of the param names to track in them (leave empty to include all).\
"""

METRICS_DESC = "List of metrics of the stage written to JSON/TOML/YAML."

PLOTS_DESC = """\
List of plots of the stage for visualization.

Plots may be written to JSON/YAML/CSV/TSV for data or JPEG/GIF/PNG for images.\
"""


class Stage(BaseModel):
    """
    A named stage of a pipeline.
    """

    cmd: str | list[str] = Field(..., description=CMD_DESC)
    wdir: str | None = Field(
        None,
        description="Working directory for the cmd, relative to `dvc.yaml`",
    )
    deps: Dependencies | None = Field(
        None, description="List of the dependencies for the stage."
    )
    params: Params | None = Field(None, description=PARAMS_DESC)
    outs: Outs | None = Field(
        None, description="List of the outputs of the stage."
    )
    metrics: Outs | None = Field(None, description=METRICS_DESC)
    plots: Plots | None = Field(None, description=PLOTS_DESC)
    frozen: bool | None = Field(False, description="Assume stage as unchanged")
    always_changed: bool | None = Field(
        False, description="Assume stage as always changed"
    )
    vars: Vars | None = Field(None, description=STAGE_VARS_DESC)
    desc: str | None = Field(None, description="Description of the stage")
    meta: Any = Field(None, description="Additional information/metadata")

    model_config = ConfigDict(extra="forbid")


FOREACH_DESC = """\
Iterable to loop through in foreach. Can be a parametrized string, list or \
a dict.

The stages will be generated by iterating through this data, by substituting \
data in the `do` block."""

DO_DESC = """\
Parametrized stage definition that'll be substituted over for each of the \
value from the foreach data."""


# class ParametrizedString(ConstrainedStr):
#     regex = re.compile(r"^\${.*?}$")

# FIXME: how to add support for regex str?
ParametrizedString = str


class ForeachDo(BaseModel):
    foreach: ParametrizedString | list[Any] | dict[str, Any] = Field(
        ..., description=FOREACH_DESC
    )
    do: Stage = Field(..., description=DO_DESC)
    model_config = ConfigDict(extra="forbid")


MATRIX_DESC = """\
Generate stages based on combination of variables.

The variable can be a list of values, or a parametrized string referencing a \
list."""


class Matrix(Stage):
    matrix: dict[str, list[Any] | ParametrizedString] = Field(
        ..., description=MATRIX_DESC
    )
    model_config = ConfigDict(extra="forbid")


Definition = ForeachDo | Matrix | Stage


VARS_DESC = """\
List of values for substitution.

May include any dict or a path to a params file which may be a string or a \
dict to params in the file).

Use elsewhere in `dvc.yaml` with the `${}` substitution expression."""


class TopLevelPlots(RootModel):
    root: dict[
        PlotIdOrFilePath, TopLevelPlotFlags | EmptyTopLevelPlotFlags
    ] = Field(default_factory=dict)


class TopLevelPlotsList(RootModel):
    root: list[PlotIdOrFilePath | TopLevelPlots] = Field(default_factory=list)


# class ArtifactIdOrFilePath(ConstrainedStr):
#     regex = re.compile(r"^[a-z0-9]([a-z0-9-/]*[a-z0-9])?$")

# FIXME: how to add support for regex str?
ArtifactIdOrFilePath = str


class TopLevelArtifacts(RootModel):
    root: dict[
        ArtifactIdOrFilePath,
        TopLevelArtifactFlags,
    ] = Field(default_factory=dict)


class DvcYamlModel(BaseModel):
    vars: Vars = Field(
        default_factory=list,
        description=VARS_DESC,
        title="Variables",
    )
    stages: dict[StageName, Definition] = Field(
        default_factory=dict,
        description="List of stages that form a pipeline.",
    )
    plots: TopLevelPlots | TopLevelPlotsList = Field(
        default_factory=dict, description="Top level plots definition."
    )
    params: set[FilePath] = Field(
        default_factory=set, description="List of parameter files"
    )
    metrics: set[FilePath] = Field(
        default_factory=set, description="List of metric files"
    )
    artifacts: TopLevelArtifacts = Field(
        default_factory=dict, description="Top level artifacts definition."
    )
    model_config = ConfigDict(title="dvc.yaml", extra="forbid")


if __name__ == "__main__":
    import json
    import sys
    from argparse import ArgumentParser, FileType

    parser = ArgumentParser()
    parser.add_argument(
        "outfile", nargs="?", type=FileType("w"), default=sys.stdout
    )

    args = parser.parse_args()
    # oneOf is expected by the JSON specification but union produces anyOf
    # https://github.com/pydantic/pydantic/issues/656
    json_data = DvcYamlModel.model_json_schema()
    out = json.dumps(json_data, indent=2).replace('"anyOf"', '"oneOf"')
    args.outfile.write(out)
    args.outfile.write("\n")
    args.outfile.close()
