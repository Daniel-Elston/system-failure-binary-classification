from __future__ import annotations

from src.core.step_definition import StepDefinition
from src.data_handling.lazy_load import LazyLoad

from src.data.process import DataPreprocessor
from src.features.build_features import BuildFeatures
from src.data.dist_transform import DistributionTransformer


def get_processing_definitions(modules: dict) -> list[StepDefinition]:
    return [
        StepDefinition(
            name="processing",
            step_class=DataPreprocessor,
            args={
                "dataset": LazyLoad(dm=modules.get("raw-data")),
            },
            # method_name="perform_data_checks"
        ),
        StepDefinition(
            name="build-features",
            step_class=BuildFeatures,
            args={
                "dataset": LazyLoad(dm=modules.get("processed-data")),
            },
            # method_name="perform_data_checks"
        ),
        StepDefinition(
            name="transform-distributions",
            step_class=DistributionTransformer,
            args={
                "dataset": LazyLoad(dm=modules.get("feature-eng")),
                "raw_data_skew_kurt": LazyLoad(dm=modules.get("raw-data-skew-kurt")),
            },
            # method_name="perform_data_checks"
        ),
    ]


    # def process(self):
    #     preprocess = [
    #         DataPreprocessor(
    #             ctx=self.ctx,
    #             dataset=self.load_data_module(self.dm_raw),
    #             module_handler=self.data_module_handler,
    #         )
    #     ]
    #     self._execute_steps(preprocess)

    #     build_features = [
    #         BuildFeatures(
    #             ctx=self.ctx,
    #             dataset=self.load_data_module(self.dm_processed),
    #             module_handler=self.data_module_handler,
    #         )
    #     ]
    #     self._execute_steps(build_features)

    #     transform = [
    #         DistributionTransformer(
    #             ctx=self.ctx,
    #             dataset=self.load_data_module(self.dm_feature_eng),
    #             module_handler=self.data_module_handler,
    #         )
    #     ]
    #     self._execute_steps(transform)
