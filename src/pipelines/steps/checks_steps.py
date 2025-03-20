from __future__ import annotations

from src.core.step_definition import StepDefinition
from src.data_handling.lazy_load import LazyLoad

from src.data.checks import ValidationChecks
from src.core.step_registry import StepRegistry


@StepRegistry.register(
    category="checks",
    name="perform-validation-checks",
    step_class=ValidationChecks,
    args={"dataset": "raw-data"},
    outputs=[],
)

def get_validation_checks_steps(modules: dict) -> list[StepDefinition]:
    return [
        StepDefinition(
            name="perform-validation-checks",
            step_class=ValidationChecks,
            args={
                "dataset": LazyLoad(dm=modules.get("raw-data")),
            },
            method_name="perform_data_checks"
        ),
    ]
