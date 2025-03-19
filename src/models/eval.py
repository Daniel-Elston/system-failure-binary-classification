from __future__ import annotations

import logging

import numpy as np
import seaborn as sns
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.model_selection import cross_val_score

from config.paths import Paths
from config.pipeline_context import PipelineContext
from config.settings import Config
from config.settings import HyperParams
from config.settings import Params
from src.core.base_pipeline import BasePipeline
from src.data_handling.data_module import DataModule
sns.set_style("darkgrid")


class EvaluateModel(BasePipeline):
    def __init__(
        self, ctx: PipelineContext,
        x_train: DataModule,
        x_test: DataModule,
        y_train: DataModule,
        y_test: DataModule,
        model: ImbPipeline,
    ):
        super().__init__(ctx)
        self.ctx = ctx
        self.best_pipeline = model
        
        self.x_train_fs = x_train
        self.x_test_fs = x_test
        self.y_train = y_train
        self.y_test = y_test
        
        self.model = model
        self.config: Config = ctx.settings.config
        self.paths: Paths = ctx.paths
        self.params: Params = ctx.settings.params
        self.hyperparams: HyperParams = ctx.settings.hyperparams

    def run(self):
        """Loads the best pipeline from disk and the already feature-selected test set, then evaluates the model."""
        self.cross_validate(self.x_train_fs, self.y_train)
        y_test_pred = self.evaluate_model()
        if not hasattr(self.best_pipeline, "predict"):
            raise ValueError("Pipeline has not been trained before cross-validation.")
        return {"y-test-pred": y_test_pred}

    def cross_validate(self, X_train, y_train):
        """Performs cross-validation and logs results."""
        scores = cross_val_score(
            self.best_pipeline,
            X_train,
            y_train,
            scoring='f1',
            cv=self.hyperparams.cv_folds
        )
        logging.debug(f"Cross-validated F1 scores (best pipeline): {scores}")
        logging.debug(f"Mean F1 Score: {np.mean(scores):.4f}")

    def evaluate_model(self):
        """Evaluates the trained model on the test set."""
        assert "feature_selector" not in dict(self.model.steps), "Feature selector should not be in final model."
        y_test_pred = self.model.predict(self.x_test_fs.to_numpy())
        return y_test_pred
