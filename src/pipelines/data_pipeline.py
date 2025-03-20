from __future__ import annotations

from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from config.pipeline_context import PipelineContext
from src.core.step_handler import StepHandler


class DataPipeline(BasePipeline):
    def __init__(self, ctx: PipelineContext):
        super().__init__(ctx)
        self.modules = {
            'raw-data': self.dm_handler.get_dm('raw-data'),
            'processed-data': self.dm_handler.get_dm('processed-data'),
            'feature-eng': self.dm_handler.get_dm('feature-eng'),
            'raw-data-skew-kurt': self.dm_handler.get_dm('raw-data-skew-kurt'),
        }

    def process(self):
        step_defs = StepHandler.get_step_defs("processing", self.modules)
        step_map = StepHandler.create_step_map(step_defs)
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
        factory = StepFactory(ctx=self.ctx, step_map=step_map)
        factory.run_pipeline(step_order, save_points)
