from __future__ import annotations

from typing import Any, Dict, List
from collections import defaultdict
from functools import wraps


class StepRegistry:
    """
    A simple class-level registry for storing step metadata at import time.
    Each step's metadata (category, name, outputs, args) is recorded via a decorator.
    """
    _registry: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    @classmethod
    def register(
        cls,
        category: str,
        name: str,
        step_class: Any,
        args: Dict[str, Any],
        outputs: List[str],
    ):
        """
        Decorator that attaches step metadata (import-time) to the registry.
        """
        def decorator(fn):
            # Record the metadata at import time
            metadata = {
                "step_n": len(cls._registry[category]) + 1,
                "name": name,
                "step_class": step_class.__name__,
                "args": args,
                "outputs": outputs,
                # leave a blank line
            }
            cls._registry[category].append(metadata)

            # Return the original function unmodified
            @wraps(fn)
            def wrapper(*inner_args, **inner_kwargs):
                return fn(*inner_args, **inner_kwargs)
            return wrapper
        return decorator

    @classmethod
    def list_all_steps(cls) -> Dict[str, List[Dict[str, Any]]]:
        return dict(cls._registry)







# from typing import Any, Callable, Dict, List

# from src.core.step_definition import StepDefinition

# from src.pipelines.steps import (
#     checks_steps,
#     evaluation_steps,
#     exploration_steps,
#     processing_steps,
#     training_steps,
# )


# class StepRegistry:
#     """
#     Central registry for retrieving step definitions from various modules
#     (checks_steps, evaluation_steps, etc.) using simple category strings.
#     """
#     _step_to_func: Dict[str, Callable[..., List[StepDefinition]]] = {
#         "validation": checks_steps.get_validation_checks_steps,
#         "exploration": exploration_steps.get_exploration_steps,
#         "processing": processing_steps.get_processing_steps,
#         "training": training_steps.get_training_steps,
#         "evaluation": evaluation_steps.get_evaluation_steps,
#     }

#     @classmethod
#     def get_definitions(cls, category: str, *args: Any, **kwargs: Any) -> List[StepDefinition]:
#         """
#         Retrieve StepDefinition objects for a given category, passing any extra args/kwargs
#         to the underlying function.
#         """
#         func = cls._step_to_func.get(category)
#         if not func:
#             valid = list(cls._step_to_func.keys())
#             raise ValueError(f"Invalid category '{category}'. Valid options are: {valid}")
#         return func(*args, **kwargs)

#     @classmethod
#     def list_all_steps(cls, *args: Any, **kwargs: Any) -> Dict[str, List[Dict[str, Any]]]:
#         """
#         Return a structured overview of all steps across every known category.
#         Each category function is called with the same *args and **kwargs.
#         """
#         steps_info: Dict[str, List[Dict[str, Any]]] = {}
#         for category, func in cls._step_to_func.items():
#             try:
#                 definitions = func(*args, **kwargs)
#                 steps_info[category] = [
#                     {
#                         "name": step.name,
#                         "args": list(step.args.keys()),
#                         "outputs": step.outputs,
#                     }
#                     for step in definitions
#                 ]
#             except Exception as e:
#                 steps_info[category] = [
#                     {"error": f"Error in {category}: {str(e)}"}
#                 ]
#         return steps_info
