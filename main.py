from __future__ import annotations

import logging

from config.pipeline_context import PipelineContext
from src.core.step_handling.step_factory import StepFactory
from src.pipelines.data_pipeline import DataPipeline
from src.pipelines.eda_pipeline import EDAPipeline
from src.pipelines.model_pipeline import ModelPipeline
from src.pipelines.steps.steps_debugger import debug_steps
from src.pipelines.validation_pipeline import ValidationPipeline
from utils.project_setup import initialise_project_configs
# from pprint import pprint
# from src.core.step_registry import StepRegistry
# from src.pipelines.steps.training_steps import get_training_steps


class MainPipeline:
    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx

    def run(self):
        """ETL pipeline main entry point."""
        steps = [
            ValidationPipeline(self.ctx).validate_names,
            EDAPipeline(self.ctx).initial_exploration,
            DataPipeline(self.ctx).process,
            EDAPipeline(self.ctx).further_exploration,
            ModelPipeline(self.ctx).train,
            ModelPipeline(self.ctx).evaluate
        ]
        StepFactory(self.ctx).run_main(steps)
        debug_steps()

        # pprint(StepRegistry.list_all_steps())


if __name__ == "__main__":
    ctx = initialise_project_configs()
    try:
        logging.info(f"Beginning Top-Level Pipeline from ``main.py``...\n{"=" * 125}")
        MainPipeline(ctx).run()
    except Exception as e:
        logging.error(f"{e}", exc_info=False)
