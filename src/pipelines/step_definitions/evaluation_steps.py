from __future__ import annotations

from src.core.step_definition import StepDefinition
from src.data_handling.lazy_load import LazyLoad

from src.models.eval import EvaluateModel
from src.plots.visuals import EvaluationVisuals


def get_evaluation_definitions(modules: dict) -> list[StepDefinition]:
    return [
        StepDefinition(
            name="evaluate-model",
            step_class=EvaluateModel,
            args={
                "x_train": LazyLoad(dm=modules.get("x-train-selected")),
                "x_test": LazyLoad(dm=modules.get("x-test-selected")),
                "y_train": LazyLoad(dm=modules.get("y-train")),
                "y_test": LazyLoad(dm=modules.get("y-test")),
                'model': LazyLoad(dm=modules.get("model")),
            },
            # method_name="perform_data_checks"
        ),
        StepDefinition(
            name="evaluation-visuals",
            step_class=EvaluationVisuals,
            args={
                "x_test": LazyLoad(dm=modules.get("x-test-selected")),
                "y_test": LazyLoad(dm=modules.get("y-test")),
                "y_test_pred": LazyLoad(dm=modules.get("y-test-pred")),
                "model": LazyLoad(dm=modules.get("model")),
                "path_key": "evaluation"
            },
            # method_name="perform_data_checks"
        ),
    ]
