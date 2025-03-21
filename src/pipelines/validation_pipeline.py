from __future__ import annotations

from config.pipeline_context import PipelineContext
from src.core.base_pipeline import BasePipeline
from src.core.step_handling.step_factory import StepFactory
from src.core.step_handling.step_handler import StepHandler


class ValidationPipeline(BasePipeline):
    """
    Summary
    ----------
    Performs data integrity checks on raw data

    Execution Flow
    ----------
    1. Loads data modules through DataModuleHandler
    2. Retrieves validation step definitions via StepHandler
    3. Executes validation checks via StepFactory
    4. Outputs invalid records to name-errors path
    """

    def __init__(self, ctx: PipelineContext):
        super().__init__(ctx)
        self.modules = {
            'raw-data': self.dm_handler.get_dm('raw-data'),
        }

    def validate_names(self):
        step_defs = StepHandler.get_step_defs("validation", self.modules)
        step_map = StepHandler.create_step_map(step_defs)
        step_order = ["perform-validation-checks"]
        save_points = []
        factory = StepFactory(ctx=self.ctx, step_map=step_map)
        factory.run_pipeline(step_order, save_points)
