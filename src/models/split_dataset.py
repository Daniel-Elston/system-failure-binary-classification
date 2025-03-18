from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from config.paths import Paths
from config.pipeline_context import PipelineContext
from config.settings import Config
from config.settings import HyperParams
from config.settings import Params
from src.data_handling.data_module import DataModule


class DatasetSplitter:
    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
    ):
        self.ctx = ctx
        self.dataset = dataset
        self.config: Config = ctx.settings.config
        self.params: Params = ctx.settings.params
        self.hyperparams: HyperParams = ctx.settings.hyperparams
        self.paths: Paths = ctx.paths

    def split(self):
        X_train, X_test, y_train, y_test = self.split_dataset(self.dataset)
        steps = [
            ('x-train', X_train),
            ('x-test', X_test),
            ('y-train', y_train),
            ('y-test', y_test),
        ]
        to_save = {}
        for path_key, data in steps:
            to_save[path_key] = data
            # self.module_handler.save_data(path_key, data)
        return to_save

    def split_dataset(self, df: pd.DataFrame):
        X = df.drop(columns=['target'])
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.hyperparams.test_size,
            stratify=y,
            random_state=self.config.random_state
        )

        if self.hyperparams.remove_outliers:
            train_df = X_train.copy()
            train_df['target'] = y_train
            train_df_clean = self._remove_iqr_outliers(train_df)
            X_train = train_df_clean.drop(columns=['target'])
            y_train = train_df_clean['target']
        return X_train, X_test, y_train, y_test

    def _remove_iqr_outliers(self, df):
        df_clean = df.copy()
        for col in df.select_dtypes(include=np.number).columns:
            q_low = df[col].quantile(self.config.iqr_upper)
            q_high = df[col].quantile(self.config.iqr_lower)
            df_clean = df_clean[(df_clean[col] >= q_low) & (df_clean[col] <= q_high)]
        logging.debug(f"Removed {len(df) - len(df_clean)} outlier rows")
        return df_clean
