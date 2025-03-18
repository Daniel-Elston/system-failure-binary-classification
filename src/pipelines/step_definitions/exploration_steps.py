from __future__ import annotations

from src.core.step_definition import StepDefinition
from src.data_handling.lazy_load import LazyLoad

from src.data.exploration import DataQualityChecks
from src.data.metadata import CollectMetadata
from src.plots.visuals import ExploratoryVisuals


def get_exploration_definitions(modules: dict, path_key: str) -> list[StepDefinition]:
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
