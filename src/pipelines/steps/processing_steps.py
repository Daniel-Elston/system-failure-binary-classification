from __future__ import annotations

from src.core.step_definition import StepDefinition
from src.data_handling.lazy_load import LazyLoad

from src.data.process import DataPreprocessor
from src.features.build_features import BuildFeatures
from src.data.dist_transform import DistributionTransformer


def get_processing_steps(modules: dict) -> list[StepDefinition]:
    return [
        StepDefinition(
            name="processing",
            step_class=DataPreprocessor,
            args={
                "dataset": LazyLoad(dm=modules.get("raw-data")),
            },
            outputs=["processed-data"]
        ),
        StepDefinition(
            name="build-features",
            step_class=BuildFeatures,
            args={
                "dataset": LazyLoad(dm=modules.get("processed-data")),
            },
            outputs=["feature-eng"]
        ),
        StepDefinition(
            name="transform-distributions",
            step_class=DistributionTransformer,
            args={
                "dataset": LazyLoad(dm=modules.get("feature-eng")),
                "raw_data_skew_kurt": LazyLoad(dm=modules.get("raw-data-skew-kurt")),
            },
            outputs=["transformed-data"]
        ),
    ]
