from __future__ import annotations

from src.core.step_handling.step_definition import StepDefinition
from src.core.data_handling.lazy_load import LazyLoad

from src.data.exploration import DataQualityChecks
from src.data.metadata import CollectMetadata
from src.plots.visuals import ExploratoryVisuals
from src.core.step_handling.step_registry import StepRegistry


@StepRegistry.register(
    category="exploration",
    name="generate-visuals",
    step_class=ExploratoryVisuals,
    args={"dataset": "raw-data", "path_key": "Optional[raw-data, transformed-data]"},
    outputs=[],
)
@StepRegistry.register(
    category="exploration",
    name="perform-quality-checks",
    step_class=DataQualityChecks,
    args={"dataset": "raw-data", "path_key": "Optional[raw-data, transformed-data]"},
    outputs=["raw-data-skew-kurt"],
)
@StepRegistry.register(
    category="exploration",
    name="collect-metadata",
    step_class=CollectMetadata,
    args={"dataset": "raw-data", "path_key": "Optional[raw-data, transformed-data]"},
    outputs=[],
)

def get_exploration_steps(modules: dict, path_key: str) -> list[StepDefinition]:
    return [
        StepDefinition(
            name="collect-metadata",
            step_class=CollectMetadata,
            args={
                "dataset": LazyLoad(dm=modules.get(path_key)),
                "path_key": path_key
            },
        ),
        StepDefinition(
            name="perform-quality-checks",
            step_class=DataQualityChecks,
            args={
                "dataset": LazyLoad(dm=modules.get(path_key)),
                "path_key": path_key
            },
            outputs=f"{path_key}-skew-kurt"
        ),
        StepDefinition(
            name="generate-visuals",
            step_class=ExploratoryVisuals,
            args={
                "dataset": LazyLoad(dm=modules.get(path_key)),
                "path_key": path_key
            },
        ),
    ]
