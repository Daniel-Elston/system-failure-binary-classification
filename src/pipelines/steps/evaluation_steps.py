from __future__ import annotations

from src.core.step_handling.step_definition import StepDefinition
from src.core.data_handling.lazy_load import LazyLoad

from src.models.eval import EvaluateModel
from src.plots.visuals import EvaluationVisuals
from src.core.step_handling.step_registry import StepRegistry


@StepRegistry.register(
    category="evaluation",
    name="evaluation-visuals",
    step_class=EvaluationVisuals,
    args={
        "x_test": "x-test-selected",
        "y_test": "y-test",
        "y_test_pred": "y-test-pred",
        "model": "model",
        "path_key": "evaluation"
    },
    outputs=[],
)
@StepRegistry.register(
    category="evaluation",
    name="evaluate-model",
    step_class=EvaluateModel,
    args={
        "x_train": "x-train-selected",
        "x_test": "x-test-selected",
        "y_train": "y-train",
        "y_test": "y-test",
        'model': "model",
    },
    outputs=["y-test-pred"],
)


def get_evaluation_steps(modules: dict) -> list[StepDefinition]:
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
            outputs=["y-test-pred"],
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
        ),
    ]
