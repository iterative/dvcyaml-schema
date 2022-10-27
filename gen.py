#!/usr/bin/env python3
"""schema.json generator."""

from typing import Any, Dict, List, NewType, Optional, Set, Union

from pydantic import BaseModel, Field, constr

# aliases
FilePath = NewType("FilePath", str)
VarKey = NewType("VarKey", str)
StageName = NewType("StageName", str)
PlotIdOrFilePath = NewType("PlotIdOrFilePath", str)
PlotColumn = NewType("PlotColumn", str)
PlotColumns = Union[str, Set[PlotColumn]]
PlotTemplateName = NewType("PlotTemplateName", str)

Template = Union[PlotTemplateName, FilePath]


class OutFlags(BaseModel):
    cache: Optional[bool] = Field(True, description="Cache output by DVC")
    persist: Optional[bool] = Field(
        False, description="Persist output between runs"
    )
    checkpoint: Optional[bool] = Field(
        False,
        description="Indicate that the output is associated with "
        "in-code checkpoints",
    )
    desc: Optional[str] = Field(
        None,
        description="User description for the output",
        title="Description",
    )
    type: Optional[str] = Field(
        None,
        description="User assigned type of the output",
        title="Type",
    )
    labels: Optional[Set[str]] = Field(
        default_factory=set,
        description="User assigned labels of the output",
        title="Labels",
    )
    meta: Optional[Dict[str, Any]] = Field(
        None, description="Custom metadata of the output.", title="Meta"
    )

    class Config:
        extra = "forbid"


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


class TopLevelPlotFlags(BaseModel):
    x: PlotColumn = Field(
        None, description="Default field name to use as x-axis data"
    )
    y: Union[PlotColumns, Dict[FilePath, PlotColumns]] = Field(
        default_factory=dict,
        description=(
            "A single column name, list of columns,"
            " or a dictionary of data-source and column pair"
        ),
    )
    x_label: str = Field(None, description="Default label for the x-axis")
    y_label: str = Field(None, description="Default label for the y-axis")
    title: str = Field(None, description="Default plot title")
    template: Template = Field(
        default="linear", description="Default plot template"
    )

    class Config:
        extra = "forbid"


class EmptyTopLevelPlotFlags(BaseModel):
    __root__: None = None


DEP_DESC = "Path to a dependency (input) file or directory for the stage."


class DepModel(BaseModel):
    __root__: FilePath = Field(..., description=DEP_DESC)


class Dependencies(BaseModel):
    __root__: Set[DepModel]


class ParamKey(BaseModel):
    __root__: str = Field(..., desc="Parameter name (dot-separated).")


class CustomParamFileKeys(BaseModel):
    __root__: Dict[FilePath, Set[ParamKey]] = Field(
        ..., desc="Path to YAML/JSON/TOML/Python params file."
    )


class EmptyParamFileKeys(BaseModel):
    __root__: Dict[FilePath, None] = Field(
        ..., desc="Path to YAML/JSON/TOML/Python params file."
    )


class Param(BaseModel):
    __root__: Union[ParamKey, CustomParamFileKeys, EmptyParamFileKeys]


class Params(BaseModel):
    __root__: Set[Param]


class Out(BaseModel):
    __root__: Union[FilePath, Dict[FilePath, OutFlags]] = Field(
        ..., description="Path to an output file or dir of the stage."
    )


class Outs(BaseModel):
    __root__: Set[Out]


class Metric(BaseModel):
    __root__: Union[FilePath, Dict[FilePath, OutFlags]] = Field(
        ...,
        description="Path to a JSON/TOML/YAML metrics output of the stage.",
    )


PLOT_DESC = """\
Path to plots file or dir of the stage.

Data files may be JSON/YAML/CSV/TSV.

Image files may be JPEG/GIF/PNG."""


class Plot(BaseModel):
    __root__: Union[FilePath, Dict[FilePath, PlotFlags]] = Field(
        ..., description=PLOT_DESC
    )


class Plots(BaseModel):
    __root__: Set[Plot]


class LiveFlags(PlotFlags):
    summary: bool = Field(
        True, description="Signals dvclive to dump latest metrics file"
    )
    html: bool = Field(
        True, description="Signals dvclive to produce training report"
    )
    cache: Optional[bool] = Field(True, description="Cache output by DVC")


class Live(BaseModel):
    __root__: Dict[FilePath, LiveFlags]

    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], _) -> None:
            """Limit no. of keys to just 1 for the Live."""
            schema["maxProperties"] = 1


class VarPath(BaseModel):
    __root__: str = Field(
        ..., description="Path to params file with values for substitution."
    )


class VarDecl(BaseModel):
    # {"foo" (str) : "foobar" (Any) }
    __root__: Dict[VarKey, Any] = Field(
        ..., description="Dict of values for substitution."
    )


class Vars(BaseModel):
    __root__: List[Union[VarPath, VarDecl]]


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

    cmd: Union[str, List[str]] = Field(..., description=CMD_DESC)
    wdir: Optional[str] = Field(
        None,
        description="Working directory for the cmd, relative to `dvc.yaml`",
    )
    deps: Optional[Dependencies] = Field(
        None, description="List of the dependencies for the stage."
    )
    params: Optional[Params] = Field(None, description=PARAMS_DESC)
    outs: Optional[Outs] = Field(
        None, description="List of the outputs of the stage."
    )
    metrics: Optional[Outs] = Field(None, description=METRICS_DESC)
    plots: Optional[Plots] = Field(None, description=PLOTS_DESC)
    live: Optional[Live] = Field(
        default_factory=list,
        description="Declare output as dvclive",
        title="Dvclive",
    )
    frozen: Optional[bool] = Field(
        False, description="Assume stage as unchanged"
    )
    always_changed: Optional[bool] = Field(
        False, description="Assume stage as always changed"
    )
    vars: Optional[Vars] = Field(None, description=STAGE_VARS_DESC)
    desc: Optional[str] = Field(None, description="Description of the stage")
    meta: Any = Field(None, description="Additional information/metadata")

    class Config:
        allow_mutation = False
        extra = "forbid"


FOREACH_DESC = """\
Iterable to loop through in foreach. Can be a parametrized string, list or \
a dict.

The stages will be generated by iterating through this data, by substituting \
data in the `do` block."""

DO_DESC = """\
Parametrized stage definition that'll be substituted over for each of the \
value from the foreach data."""


ParametrizedString = constr(regex=r"^\${.*?}$")


class ForeachDo(BaseModel):
    foreach: Union[ParametrizedString, List[Any], Dict[str, Any]] = Field(
        ..., description=FOREACH_DESC
    )
    do: Stage = Field(..., description=DO_DESC)

    class Config:
        extra = "forbid"


Definition = Union[ForeachDo, Stage]


VARS_DESC = """\
List of values for substitution.

May include any dict or a path to a params file which may be a string or a \
dict to params in the file).

Use elsewhere in `dvc.yaml` with the `${}` substitution expression."""


class DvcYamlModel(BaseModel):
    vars: Vars = Field(
        default_factory=list,
        description=VARS_DESC,
        title="Variables",
    )
    stages: Dict[StageName, Definition] = Field(
        default_factory=dict,
        description="List of stages that form a pipeline.",
    )
    plots: Union[
        List[
            Union[
                PlotIdOrFilePath,
                Dict[
                    PlotIdOrFilePath,
                    Union[TopLevelPlotFlags, EmptyTopLevelPlotFlags],
                ]
            ]
        ],
        Dict[
            PlotIdOrFilePath, Union[TopLevelPlotFlags, EmptyTopLevelPlotFlags]
        ],
    ] = Field(default_factory=dict, description="Top level plots definition.")

    class Config:
        title = "dvc.yaml"
        extra = "forbid"

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _) -> None:
            """Make foreach-do/stage either-or."""
            for item in ["properties", "stages", "additionalProperties"]:
                schema = schema.get(item, {})
            schema["oneOf"] = schema.pop("anyOf")


if __name__ == "__main__":
    print(DvcYamlModel.schema_json(indent=2))
