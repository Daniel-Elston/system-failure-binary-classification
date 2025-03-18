from __future__ import annotations

from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from src.core.step_definition import create_step_map
from config.pipeline_context import PipelineContext
from src.pipelines.step_definitions.training_steps import get_training_definitions
from src.pipelines.step_definitions.evaluation_steps import get_evaluation_definitions

from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

# from src.models.eval import EvaluateModel
from src.models.split_dataset import DatasetSplitter
from src.models.trainer import ModelTrainer
# from src.plots.visuals import EvaluationVisuals


class ModelPipeline(BasePipeline):
    def __init__(self, ctx: PipelineContext):
        super().__init__(ctx)
        self.modules = {
            'transformed-data': self.create_data_module('transformed-data'),
            'x-train': self.create_data_module('x-train'),
            'x-test': self.create_data_module('x-test'),
            'y-train': self.create_data_module('y-train'),
            'y-test': self.create_data_module('y-test'),
            'model': self.create_data_module('model'),
            'x-train-selected': self.create_data_module('x-train-selected'),
            'x-test-selected': self.create_data_module('x-test-selected'),
            'y-test-pred': self.create_data_module('y-test-pred')
        }
        estimator = RandomForestClassifier(
            n_estimators=100,
            random_state=self.config.random_state
        )
        self.feature_selector = SelectFromModel(
            estimator=estimator,
            threshold="median"
        )
        self.pipeline_builder = ImbPipeline(
            steps=[
                ('feature_selector', self.feature_selector),
                ('scaler', StandardScaler()),
                ("sampler", self.params.get_sampler()),
                ('classifier', self.params.get_model())
            ]
        )
        self.skf = StratifiedKFold(
            n_splits=self.hyperparams.cv_folds,
            shuffle=True,
            random_state=self.config.random_state
        )

    def train(self):
        run_model_definitions = get_training_definitions(self.modules, self.pipeline_builder, self.skf)
        step_order = ["split-dataset", "train-model"]
        save_points = ["split-dataset", "train-model"]
        factory = StepFactory(ctx=self.ctx, step_map=create_step_map(run_model_definitions))
        factory.run_pipeline(step_order, save_points)

    def evaluate(self):
        run_model_definitions = get_evaluation_definitions(self.modules)
        step_order = ["evaluate-model", "evaluation-visuals"]
        save_points = ["evaluate-model"]#, "evaluation-visuals"]
        factory = StepFactory(ctx=self.ctx, step_map=create_step_map(run_model_definitions))
        factory.run_pipeline(step_order, save_points)




# class ModelPipeline(BasePipeline):
#     def __init__(
#         self, ctx: PipelineContext,
#     ):
#         super().__init__(ctx)
#         self.transformed = self.create_data_module(path_key="transformed-data")
#         self.dm_model = self.create_data_module(path_key="model")

#         self.feature_selector = SelectFromModel(
#             estimator=RandomForestClassifier(
#                 n_estimators=100,
#                 random_state=self.config.random_state
#             ),
#             threshold="median"
#         )
#         self.pipeline_builder = ImbPipeline(
#             steps=[
#                 ('feature_selector', self.feature_selector),
#                 ('scaler', StandardScaler()),
#                 ("sampler", self.params.get_sampler()),
#                 ('classifier', self.params.get_model())
#             ]
#         )
#         self.skf = StratifiedKFold(
#             n_splits=self.hyperparams.cv_folds,
#             shuffle=True,
#             random_state=self.config.random_state
#         )

#     def train_and_evaluate(self):
#         training = [
#             DatasetSplitter(
#                 ctx=self.ctx,
#                 dataset=self.load_data_module(self.transformed),
#                 module_handler=self.data_module_handler,
#             ),
#             ModelTrainer(
#                 ctx=self.ctx,
#                 module_handler=self.data_module_handler,
#                 pipeline_builder=self.pipeline_builder,
#                 skf=self.skf
#             ),
#         ]
#         self._execute_steps(training)

#         evaluation = [
#             EvaluateModel(
#                 ctx=self.ctx,
#                 model=self.load_data_module(self.dm_model),
#                 module_handler=self.data_module_handler,
#             ),
#             EvaluationVisuals(
#                 ctx=self.ctx,
#                 model=self.load_data_module(self.dm_model),
#                 path_key="evaluation"
#             )
#         ]
#         self._execute_steps(evaluation)
