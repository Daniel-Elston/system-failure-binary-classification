from __future__ import annotations

from collections import defaultdict
from functools import wraps
from typing import Any
from typing import Dict
from typing import List


class StepRegistry:
    """
    Summary
    ----------
    Central catalog for pipeline step configurations
    Maintains import-time metadata about pipeline steps using class decorators.
    Enables discovery of available steps and their configurations.

    Extended Summary
    ----------
    - Uses decorator-based registration at module import time
    - Organizes steps by category (e.g., 'preprocessing', 'modeling')
    - Stores metadata including arguments, outputs, and execution order
    - Provides complete registry inspection via list_all_steps()

    Returns
    -------
    Dict[str, List[Dict[str, Any]]]
        Category-keyed dictionary of step metadata when using list_all_steps()
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
        Registers step metadata in the global registry
        Decorator that records step configuration during module import.
        """
        def decorator(fn):
            # Record the metadata at import time
            metadata = {
                "name": name,
                "substep_n": len(cls._registry[category]) + 1,
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
        """
        Retrieves complete step registry at import time
        Provides snapshot of all registered steps organized by category.
        """
        return dict(cls._registry)
