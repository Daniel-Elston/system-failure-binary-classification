from __future__ import annotations

from config.pipeline_context import PipelineContext
from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from src.core.step_definition import create_step_map
from src.pipelines.steps.checks_steps import get_validation_checks_steps


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
            'raw-data': self.create_data_module('raw-data'),
        }

    def validate_names(self):
        validation_definitions = get_validation_checks_steps(self.modules)
        step_order = ["perform-validation-checks"]
        save_points = []
        factory = StepFactory(ctx=self.ctx, step_map=create_step_map(validation_definitions))
        factory.run_pipeline(step_order, save_points)
