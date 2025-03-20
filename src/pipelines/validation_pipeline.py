from __future__ import annotations

from config.pipeline_context import PipelineContext
from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from src.core.step_handler import StepHandler


class ValidationPipeline(BasePipeline):
    """
    Summary: Applies raw mapping and validates result\n
    Brief:
        - Use most up-to-date names in mapping
        - Validate that mapping is correct and identify name-errors (NaNs)
        - Store name-errors in a file separated from correct logs\n
    Output: Dataset containing only exercise names not present in mapping
    Output Path Idx: name-errors
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
