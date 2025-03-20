from __future__ import annotations

from src.core.base_pipeline import BasePipeline
from src.core.step_factory import StepFactory
from config.pipeline_context import PipelineContext
from src.core.step_handler import StepHandler

from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler



class ModelPipeline(BasePipeline):
    def __init__(self, ctx: PipelineContext):
        super().__init__(ctx)
        self.modules = {
            'transformed-data': self.dm_handler.get_dm('transformed-data'),
            'x-train': self.dm_handler.get_dm('x-train'),
            'x-test': self.dm_handler.get_dm('x-test'),
            'y-train': self.dm_handler.get_dm('y-train'),
            'y-test': self.dm_handler.get_dm('y-test'),
            'model': self.dm_handler.get_dm('model'),
            'x-train-selected': self.dm_handler.get_dm('x-train-selected'),
            'x-test-selected': self.dm_handler.get_dm('x-test-selected'),
            'y-test-pred': self.dm_handler.get_dm('y-test-pred')
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
        step_defs = StepHandler.get_step_defs("training", self.modules, self.pipeline_builder, self.skf)
        step_map = StepHandler.create_step_map(step_defs)
        step_order = ["split-dataset", "train-model"]
        save_points = ["split-dataset", "train-model"]
        factory = StepFactory(ctx=self.ctx, step_map=step_map)
        factory.run_pipeline(step_order, save_points)

    def evaluate(self):
        step_defs = StepHandler.get_step_defs("evaluation", self.modules)
        step_map = StepHandler.create_step_map(step_defs)
        step_order = ["evaluate-model", "evaluation-visuals"]
        save_points = ["evaluate-model"]
        factory = StepFactory(ctx=self.ctx, step_map=step_map)
        factory.run_pipeline(step_order, save_points)
