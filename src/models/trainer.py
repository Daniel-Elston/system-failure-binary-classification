from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.metrics import f1_score
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import StratifiedKFold

from config.pipeline_context import PipelineContext
from config.settings import Config
from config.settings import HyperParams
from src.core.base_pipeline import BasePipeline
from src.core.data_handling.data_module import DataModule


class ModelTrainer(BasePipeline):
    """Handles training and model selection using hyperparameter tuning."""

    def __init__(
        self, ctx: PipelineContext,
        x_train: DataModule,
        x_test: DataModule,
        y_train: DataModule,
        y_test: DataModule,
        pipeline_builder: ImbPipeline,
        skf: StratifiedKFold
    ):
        super().__init__(ctx)
        self.ctx = ctx
        self.config: Config = ctx.settings.config
        self.hyperparams: HyperParams = ctx.settings.hyperparams

        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.pipeline_builder = pipeline_builder
        self.skf = skf

    def run(self):
        y_train = self.y_train.values.ravel()
        # y_test = self.y_test.values.ravel()
        model, selected_indices = self.train_model(self.x_train, y_train)

        x_train_selected = self.x_train.iloc[:, selected_indices]
        x_test_selected = self.x_test.iloc[:, selected_indices]
        return {
            "selected-features": selected_indices,
            "x-train-selected": x_train_selected,
            "x-test-selected": x_test_selected,
            "model": model
        }

    def train_model(self, x_train: pd.DataFrame, y_train: np.ndarray):
        """Train model and remove feature selector at inference time."""
        search = RandomizedSearchCV(
            estimator=self.pipeline_builder,
            param_distributions=self.hyperparams.param_dist,
            scoring=make_scorer(f1_score),
            n_iter=20,
            cv=self.skf,
            verbose=1,
            n_jobs=-1,
            random_state=self.config.random_state
        )
        search.fit(x_train, y_train)
        best_model = search.best_estimator_

        # Extract selected features
        selected_features = best_model.named_steps["feature_selector"].get_support()
        selected_indices = np.where(selected_features)[0]

        logging.info(f"Selected {len(selected_indices)} features: {selected_indices}")

        # Remove feature selector for inference
        best_model.steps = [
            step for step in best_model.steps if step[0] != "feature_selector"
        ]
        logging.debug(f"Best params found: {search.best_params_}")
        logging.debug(f"Cross-validation best F1: {search.best_score_:.4f}")
        return best_model, selected_indices
