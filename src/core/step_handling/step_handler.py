from __future__ import annotations

from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from src.core.step_handling.step_definition import StepDefinition
from src.pipelines.steps import checks_steps
from src.pipelines.steps import evaluation_steps
from src.pipelines.steps import exploration_steps
from src.pipelines.steps import processing_steps
from src.pipelines.steps import training_steps


class StepHandler:
    """
    Summary
    -------
    Central registry for pipeline step definitions
    Provides unified access to step configurations across different pipeline stages.
    Converts modular step definitions into StepFactory-compatible format.

    Extended Summary
    ----------
    - Maintains category-to-retrieval-function mapping
    - Validates category requests
    - Transforms StepDefinition objects into factory configuration format

    Returns
    -------
    dict
        StepFactory-compatible mapping when using create_step_map()

    Raises
    ------
    ValueError
        When requesting undefined category
    """
    _step_to_func: Dict[str, Callable] = {
        "validation": checks_steps.get_validation_checks_steps,
        "exploration": exploration_steps.get_exploration_steps,
        "processing": processing_steps.get_processing_steps,
        "training": training_steps.get_training_steps,
        "evaluation": evaluation_steps.get_evaluation_steps,
    }

    @classmethod
    def get_step_defs(cls, category: str, *args: Any, **kwargs: Any) -> List[StepDefinition]:
        """
        Retrieves step definitions for a pipeline stage
        Returns configured StepDefinitions for requested category,
        forwarding any additional arguments to the definition getter.
        """
        func = cls._step_to_func.get(category)
        if not func:
            valid = list(cls._step_to_func.keys())
            raise ValueError(f"Invalid category '{category}'. Valid options are: {valid}")
        return func(*args, **kwargs)

    @staticmethod
    def create_step_map(definitions: List[StepDefinition]) -> dict:
        """
        Transforms StepDefinitions into StepFactory configuration
        Converts list of StepDefinition objects into dictionary
        format required by StepFactorys step_map.
        """
        return {
            step_def.name: (
                step_def.step_class,
                step_def.args,
                step_def.method_name
            )
            for step_def in definitions
        }
