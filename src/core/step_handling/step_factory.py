from __future__ import annotations

import logging
from typing import Callable
from typing import List

from src.core.base_pipeline import BasePipeline
from src.core.data_handling.lazy_load import LazyLoad
from utils.logging_utils import log_step


class StepFactory(BasePipeline):
    """
    Summary
    ----------
    Dynamic pipeline step orchestrator.
    Factory class that creates and executes pipeline steps using a configurable step mapping.
    Manages argument resolution, method dispatch, and checkpoint logging.

    Extended Summary
    ----------
    - Inherits pipeline context from BasePipeline
    - Maintains a registry of step configurations (classes, arguments, and methods)
    - Handles lazy-loaded argument resolution through DataModuleHandler
    - Supports runtime argument injection via **runtime_extra

    Outputs
    ----------
    - Initialized StepFactory instance ready to execute pipeline steps

    Parameters
    ----------
    ctx : PipelineContext
        Container for paths, settings, and pipeline states
    step_map : dict, optional
        Preconfigured step definitions mapping step names to
        (StepClass, base_args, method_name) tuples
    """

    def __init__(self, ctx, step_map=None):
        super().__init__(ctx)
        self.ctx = ctx
        self.step_map: dict = step_map or {}

    def dispatch_step(self, step_name: str, **runtime_extra):
        """
        Resolves and executes a single pipeline step.
        Looks up step configuration, resolves lazy-loaded dependencies,
        instantiates the step class, and executes the target method.
        """
        try:
            StepClass, base_args, method_name = self.step_map[step_name]
        except KeyError:
            raise ValueError(f"Unknown step `{step_name}`. Check step definitions.")

        resolved_args = {}
        for k, v in base_args.items():
            if isinstance(v, LazyLoad):
                resolved_args[k] = v.load(self.dm_handler)
            else:
                resolved_args[k] = v

        all_args = {**resolved_args, **runtime_extra}
        instance = StepClass(ctx=self.ctx, **all_args)
        method = getattr(instance, method_name)
        return log_step()(method)()

    def run_pipeline(self, step_order: List[str], checkpoints: List[str] = None):
        """
        Executes a sequence of pipeline steps with checkpoint support
        Processes steps in specified order, saving intermediate results
        at designated checkpoints using DataModuleHandler.
        """
        checkpoints = checkpoints or []
        for step_name in step_order:
            result = self.dispatch_step(step_name)
            if step_name in checkpoints:
                logging.debug(f"SAVING at checkpoint: {step_name}")
                self.dm_handler.save_data(result)

    def run_main(self, steps: List[Callable]):
        """Applies log_step decorator to each step and executes in sequence."""
        for step in steps:
            log_step()(step)()
