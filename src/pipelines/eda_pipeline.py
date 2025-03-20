from __future__ import annotations

from config.pipeline_context import PipelineContext
from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from src.core.step_handler import StepHandler


class EDAPipeline(BasePipeline):
    def __init__(self, ctx: PipelineContext):
        super().__init__(ctx)
        self.modules = {
            'raw-data': self.dm_handler.get_dm('raw-data'),
            'transformed-data': self.dm_handler.get_dm('transformed-data'),
        }

    def initial_exploration(self):
        step_defs = StepHandler.get_step_defs("exploration", self.modules, "raw-data")
        step_map = StepHandler.create_step_map(step_defs)
        step_order = ["collect-metadata", "perform-quality-checks", "generate-visuals"]
        save_points = ["perform-quality-checks"]
        factory = StepFactory(ctx=self.ctx, step_map=step_map)
        factory.run_pipeline(step_order, save_points)

    def further_exploration(self):
        step_defs = StepHandler.get_step_defs("exploration", self.modules, "transformed-data")
        step_map = StepHandler.create_step_map(step_defs)
        step_order = ["collect-metadata", "perform-quality-checks", "generate-visuals"]
        save_points = ["perform-quality-checks"]
        factory = StepFactory(ctx=self.ctx, step_map=step_map)
        factory.run_pipeline(step_order, save_points)
