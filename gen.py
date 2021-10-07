"""schema.json generator."""

# flake8: noqa: D1
# pylint: disable=missing-class-docstring,too-few-public-methods
from typing import Any, Dict, List, NewType, Optional, Set, Union

from pydantic import BaseModel, Field, constr

# aliases
FilePath = NewType("FilePath", str)
ParamKey = NewType("ParamKey", str)
VarKey = NewType("VarKey", str)
StageName = NewType("StageName", str)


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


class PlotFlags(OutFlags):
    x: str = Field(
        None, description="Default field name to use as x-axis data"
    )
    y: str = Field(
        None, description="Default field name to use as y-axis data"
    )
    x_label: str = Field(None, description="Default label for the x-axis")
    y_label: str = Field(None, description="Default label for the y-axis")
    title: str = Field(None, description="Default plot title")
    header: bool = Field(
        False, description="Whether the target CSV or TSV has a header or not"
    )
    template: FilePath = Field(None, description="Default plot template")


class DepModel(BaseModel):
    __root__: FilePath = Field(..., description="A dependency for the stage")


class Dependencies(BaseModel):
    __root__: Set[DepModel]


class CustomParamFileKeys(BaseModel):
    __root__: Dict[FilePath, Set[ParamKey]]


class Param(BaseModel):
    __root__: Union[ParamKey, CustomParamFileKeys]


class Params(BaseModel):
    __root__: Set[Param]


class Out(BaseModel):
    __root__: Union[FilePath, Dict[FilePath, OutFlags]]


class Outs(BaseModel):
    __root__: Set[Out]


class Plot(BaseModel):
    __root__: Union[FilePath, Dict[FilePath, PlotFlags]]


class Plots(BaseModel):
    __root__: Set[Plot]


class LiveFlags(PlotFlags):
    summary: bool = Field(
        True, description="Signals dvclive to dump latest metrics file"
    )
    html: bool = Field(
        True, description="Signals dvclive to produce training report"
    )


class Live(BaseModel):
    __root__: Dict[FilePath, LiveFlags]

    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], _) -> None:
            """Limit no. of keys to just 1 for the Live."""
            schema["maxProperties"] = 1


class VarDecl(BaseModel):
    # {"foo" (str) : "foobar" (Any) }
    __root__: Dict[VarKey, Any]


class Vars(BaseModel):
    __root__: List[Union[FilePath, VarDecl]]


class Stage(BaseModel):
    cmd: Union[str, List[str]] = Field(..., description="Command to run")
    wdir: Optional[str] = Field(None, description="Working directory")
    deps: Optional[Dependencies] = Field(
        None, description="Dependencies for the stage"
    )
    params: Optional[Params] = Field(None, description="Params for the stage")
    outs: Optional[Outs] = Field(None, description="Outputs of the stage")
    metrics: Optional[Outs] = Field(None, description="Metrics of the stage")
    plots: Optional[Plots] = Field(None, description="Plots of the stage")
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
    vars: Optional[Vars] = Field(
        None, description="Variables for the parametrization"
    )
    desc: Optional[str] = Field(None, description="Description of the stage")
    meta: Any = Field(None, description="Additional information/metadata")

    class Config:
        allow_mutation = False


FOREACH_DESC = """\
Iterable to loop through in foreach. Can be a parametrized string, list \
or a dictionary.

The stages will be generated by iterating through this data, by substituting
data in the `do` block."""

DO_DESC = """\
Parametrized stage definition that'll be substituted over for each of the
value from the foreach data."""


ParametrizedString = constr(regex=r"^\${.*?}$")


class ForeachDo(BaseModel):
    foreach: Union[ParametrizedString, List[Any], Dict[str, Any]] = Field(
        ..., description=FOREACH_DESC
    )
    do: Stage = Field(..., description=DO_DESC)


Definition = Union[ForeachDo, Stage]


class DvcYamlModel(BaseModel):
    vars: Vars = Field(
        default_factory=list,
        description="Variables for the parametrization",
        title="Variables",
    )
    stages: Dict[StageName, Definition] = Field(
        default_factory=dict, description="List of stages"
    )

    class Config:
        title = "dvc.yaml"

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _) -> None:
            """Make foreach-do/stage either-or."""
            for item in ["properties", "stages", "additionalProperties"]:
                schema = schema.get(item, {})
            schema["oneOf"] = schema.pop("anyOf")


if __name__ == "__main__":
    print(DvcYamlModel.schema_json(indent=2))
