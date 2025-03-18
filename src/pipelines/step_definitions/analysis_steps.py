from __future__ import annotations

from src.core.step_definition import StepDefinition
from src.data_handling.lazy_load import LazyLoad

from src.features.build_features import SimilarityFeatureBuilder
from src.data.analysis import SimilarityAnalysis


def get_analysis_definitions(modules: dict) -> list[StepDefinition]:
    return [
        StepDefinition(
            name="feature_eng",
            step_class=SimilarityFeatureBuilder,
            args={
                "dataset": LazyLoad(dm=modules.get("match-scores-full"))
            },
            method_name="build"
        ),
        StepDefinition(
            name="analyse",
            step_class=SimilarityAnalysis,
            args={
                "dataset": LazyLoad(dm=modules.get("match-score-eng"))
            },
            method_name="analyse_match_scores"
        ),
    ]
