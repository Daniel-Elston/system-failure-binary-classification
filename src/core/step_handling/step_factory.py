from __future__ import annotations

import logging
from typing import Callable
from typing import List

from src.core.base_pipeline import BasePipeline
from src.core.data_handling.lazy_load import LazyLoad
from utils.logging_utils import log_step


class StepFactory(BasePipeline):
    def __init__(self, ctx, step_map=None):
        super().__init__(ctx)
        self.ctx = ctx
        self.step_map: dict = step_map or {}

    def dispatch_step(self, step_name: str, **runtime_extra):
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
        """Loops through each step name and dispatches to the factory."""
        checkpoints = checkpoints or []
        for step_name in step_order:
            result = self.dispatch_step(step_name)
            if step_name in checkpoints:
                logging.debug(f"SAVING at checkpoint: {step_name}")
                self.dm_handler.save_data(result)

    def run_main(self, steps: List[Callable]):
        """Decorates each step with log_step, then executes."""
        for step in steps:
            log_step()(step)()
