from __future__ import annotations

from config.pipeline_context import PipelineContext
from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from src.core.step_definition import create_step_map
from src.pipelines.step_definitions.exploration_steps import get_exploration_definitions

class EDAPipeline(BasePipeline):
    def __init__(self, ctx: PipelineContext):
        super().__init__(ctx)
        self.modules = {
            'raw-data': self.create_data_module('raw-data'),
            'transformed-data': self.create_data_module('transformed-data'),
        }

    def initial_exploration(self):
        validation_definitions = get_exploration_definitions(self.modules, "raw-data")
        step_order = ["collect-metadata", "perform-quality-checks", "generate-visuals"]
        save_points = ["perform-quality-checks"]
        factory = StepFactory(ctx=self.ctx, step_map=create_step_map(validation_definitions))
        factory.run_pipeline(step_order, save_points)

    def further_exploration(self):
        validation_definitions = get_exploration_definitions(self.modules, "transformed-data")
        step_order = [
            "collect-metadata",
            "perform-quality-checks",
            "generate-visuals"
        ]
        save_points = [
            "perform-quality-checks"
        ]
        factory = StepFactory(ctx=self.ctx, step_map=create_step_map(validation_definitions))
        factory.run_pipeline(step_order, save_points)


    # def initial_exploration(self):
    #     path_key = "raw"
    #     dm_raw = self.create_data_module(path_key)
    #     return self.explore(dm_raw, path_key)

    # def further_exploration(self):
    #     path_key = "transformed"
    #     dm_eng = self.create_data_module(path_key)
    #     return self.explore(dm_eng, path_key)

    # def explore(self, data_module, path_key):
        
    #     steps = [
    #         CollectMetadata(
    #             ctx=self.ctx,
    #             dataset=self.load_data_module(data_module),
    #             module_handler=self.data_module_handler,
    #             path_key=path_key
    #         ),
    #         DataQualityChecks(
    #             ctx=self.ctx,
    #             dataset=self.load_data_module(data_module),
    #             module_handler=self.data_module_handler,
    #             path_key=path_key
    #         ),
    #         ExploratoryVisuals(
    #             ctx=self.ctx,
    #             dataset=self.load_data_module(data_module),
    #             path_key=path_key
    #         ),
    #         ExploratoryVisuals(
    #             ctx=self.ctx,
    #             dataset=self.load_data_module(data_module),
    #             path_key=path_key
    #         ).generate_target_barplot(),
    #     ]
    #     self._execute_steps(steps)
