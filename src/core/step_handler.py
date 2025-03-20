from __future__ import annotations

import attrs
from typing import Any, Callable, Dict, List
from src.core.step_definition import StepDefinition

from src.pipelines.steps import (
    checks_steps,
    evaluation_steps,
    exploration_steps,
    processing_steps,
    training_steps,
)


class StepHandler:
    """
    Central registry for retrieving step definitions from various modules
    (checks_steps, evaluation_steps, etc.) using simple category strings.
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
        Retrieve StepDefinition objects for a given category, passing any extra args/kwargs
        to the underlying function.
        """
        func = cls._step_to_func.get(category)
        if not func:
            valid = list(cls._step_to_func.keys())
            raise ValueError(f"Invalid category '{category}'. Valid options are: {valid}")
        return func(*args, **kwargs)

    @staticmethod
    def create_step_map(definitions: List[StepDefinition]) -> dict:
        """Convert a list of StepDefinitions into a StepFactory-compatible map."""
        return {
            step_def.name: (
                step_def.step_class,
                step_def.args,
                step_def.method_name
            )
            for step_def in definitions
        }
