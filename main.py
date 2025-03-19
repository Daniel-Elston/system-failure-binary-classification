from __future__ import annotations

import logging

from config.pipeline_context import PipelineContext
from src.core.base_pipeline import BasePipeline
from src.pipelines.data_pipeline import DataPipeline
from src.pipelines.model_pipeline import ModelPipeline
from src.pipelines.validation_pipeline import ValidationPipeline
from src.pipelines.eda_pipeline import EDAPipeline
from utils.project_setup import init_project
import warnings
warnings.filterwarnings("ignore")


class MainPipeline:
    def __init__(
        self, ctx: PipelineContext,
    ):
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
        BasePipeline(self.ctx)._execute_steps(steps)


if __name__ == "__main__":
    project_dir, project_config, ctx = init_project()
    try:
        logging.info(f"Beginning Top-Level Pipeline from ``main.py``...\n{"=" * 125}")
        MainPipeline(ctx).run()
    except Exception as e:
        logging.error(f"{e}", exc_info=True)
