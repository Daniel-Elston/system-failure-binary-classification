from __future__ import annotations

import logging
from pprint import pformat

import numpy as np
import seaborn as sns

from config.pipeline_context import PipelineContext
from config.settings import Config
from src.core.data_handling.data_module import DataModule
sns.set_style("darkgrid")


class DataQualityChecks:
    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
        path_key: str
    ):
        self.ctx = ctx
        self.dataset = dataset
        self.path_key = path_key
        self.config: Config = ctx.settings.config

    def run(self):
        steps = [
            ("find_duplicates", self.find_duplicates()),
            ("find_missing_values", self.find_missing_values()),
            ("find_missing_percentage", self.find_missing_percentage()),
            ("find_unique_values", self.find_unique_values()),
            ("find_value_counts", self.find_value_counts()),
            ("target_imbalance", self.target_imbalance()),
            ("find_skewness_kurtosis", self.find_skewness_kurtosis()),
        ]
        for step_name, step_result in steps:
            logging.debug(f"{step_name}:\n {pformat(step_result)}\n")
        return {f'{self.path_key}-skew-kurt': self.find_skewness_kurtosis()}

    def find_duplicates(self):
        return len(self.dataset[self.dataset.duplicated(keep='first')])

    def find_missing_values(self):
        return self.dataset.isnull().sum()

    def find_missing_percentage(self):
        return self.dataset.isnull().sum() / len(self.dataset) * 100

    def find_unique_values(self):
        object_cols = self.dataset.select_dtypes(include=['object'])

        if object_cols.empty:
            logging.debug("Categorical columns processed")
            return None

        return object_cols.nunique()

    def find_value_counts(self):
        object_cols = self.dataset.select_dtypes(include=['object'])

        if object_cols.empty:
            logging.debug("Categorical columns processed")
            return None

        return object_cols.apply(lambda x: x.value_counts(normalize=True))

    def target_imbalance(self):
        return self.dataset[self.config.target_col].value_counts(normalize=True)

    def find_skewness_kurtosis(self):
        """Computes skewness and kurtosis for numerical columns, handling NaNs efficiently."""
        skew_kurt_store = {}
        cols = self.dataset.select_dtypes(include=np.number).columns
        for col in cols:
            data = self.dataset[col].dropna()
            skewness = float(round(data.skew(), 3))
            kurtosis = float(round(data.kurt(), 3))
            skew_kurt_store[col] = (skewness, kurtosis)
        return skew_kurt_store
