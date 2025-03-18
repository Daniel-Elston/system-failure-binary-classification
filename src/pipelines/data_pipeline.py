from __future__ import annotations

from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from src.core.step_definition import create_step_map
from config.pipeline_context import PipelineContext
from src.pipelines.step_definitions.processing_steps import get_processing_definitions


class DataPipeline(BasePipeline):
    def __init__(self, ctx: PipelineContext):
        super().__init__(ctx)
        self.modules = {
            'raw-data': self.create_data_module('raw-data'),
            'processed-data': self.create_data_module('processed-data'),
            'feature-eng': self.create_data_module('feature-eng'),
            'raw-data-skew-kurt': self.create_data_module('raw-data-skew-kurt'),
        }

    def process(self):
        initial_process_definitions = get_processing_definitions(self.modules)
        step_order = [
            "processing",
            "build-features",
            "transform-distributions"
        ]
        save_points = [
            "processing",
            "build-features",
            "transform-distributions"
        ]
        factory = StepFactory(ctx=self.ctx, step_map=create_step_map(initial_process_definitions))
        factory.run_pipeline(step_order, save_points)
