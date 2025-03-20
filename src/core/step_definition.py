from __future__ import annotations

import attrs
from typing import Type, List


@attrs.define
class StepDefinition:
    name: str
    step_class: Type
    args: dict
    method_name: str = "run"
    outputs: list[str] = attrs.field(factory=list)
