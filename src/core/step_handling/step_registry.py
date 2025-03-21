from __future__ import annotations

from collections import defaultdict
from functools import wraps
from typing import Any
from typing import Dict
from typing import List


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
        return dict(cls._registry)
