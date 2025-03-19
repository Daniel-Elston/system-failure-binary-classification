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

def create_step_map(definitions: List[StepDefinition]) -> dict:
    """Convert a list of StepDefinitions into a StepFactory-compatible map."""
    return {
        step_def.name: (step_def.step_class, step_def.args, step_def.method_name)
        for step_def in definitions
    }
