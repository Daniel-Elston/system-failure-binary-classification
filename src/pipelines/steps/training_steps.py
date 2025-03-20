from __future__ import annotations

from src.core.step_definition import StepDefinition
from src.data_handling.lazy_load import LazyLoad

from src.models.split_dataset import DatasetSplitter
from src.models.trainer import ModelTrainer
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.model_selection import StratifiedKFold

from src.core.step_registry import StepRegistry


@StepRegistry.register(
    category="training",
    name="train-model",
    step_class=ModelTrainer,
    args={
        "x_train": "x-train",
        "x_test": "x-test",
        "y_train": "y-train",
        "y_test": "y-test",
        "pipeline_builder": ImbPipeline.__name__,
        "skf": StratifiedKFold.__name__
    },
    outputs=["selected-features", "x-train-selected", "x-test-selected", "model"],
)
@StepRegistry.register(
    category="training",
    name="split-dataset",
    step_class=DatasetSplitter,
    args={"dataset": "transformed-data"},
    outputs=["x-train", "x-test", "y-train", "y-test"],
)

def get_training_steps(
    modules: dict,
    pipeline_builder: ImbPipeline,
    skf: StratifiedKFold
) -> list[StepDefinition]:
    return [
        StepDefinition(
            name="split-dataset",
            step_class=DatasetSplitter,
            args={
                "dataset": LazyLoad(dm=modules.get("transformed-data")),
            },
            method_name="split",
            outputs=["x-train", "x-test", "y-train", "y-test"]
        ),
        StepDefinition(
            name="train-model",
            step_class=ModelTrainer,
            args={
                "x_train": LazyLoad(dm=modules.get("x-train")),
                "x_test": LazyLoad(dm=modules.get("x-test")),
                "y_train": LazyLoad(dm=modules.get("y-train")),
                "y_test": LazyLoad(dm=modules.get("y-test")),
                "pipeline_builder": pipeline_builder,
                "skf": skf
            },
            method_name="run",
            outputs=["selected-features", "x-train-selected", "x-test-selected", "model"]
        ),
    ]
