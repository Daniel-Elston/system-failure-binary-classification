from __future__ import annotations

import numpy as np
import seaborn as sns
from scipy.stats import boxcox
from scipy.stats import yeojohnson

from config.paths import Paths
from config.pipeline_context import PipelineContext
from config.settings import Config
from src.data_handling.data_module import DataModule
sns.set_style("darkgrid")


class DistributionTransformer:
    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
        raw_data_skew_kurt: DataModule
    ):
        self.ctx = ctx
        self.dataset = dataset
        self.raw_data_skew_kurt = raw_data_skew_kurt
        
        self.config: Config = ctx.settings.config
        self.paths: Paths = ctx.paths

        self.log_skew_threshold = self.config.log_skew_threshold
        self.kurtosis_threshold = self.config.kurtosis_threshold
        self.boxcox_skew_threshold = self.config.boxcox_skew_threshold
        self.yeo_johnson_skew_threshold = self.config.yeo_johnson_skew_threshold

    def run(self):
        df_transform = self.assign_transform()
        df = self.apply_transform(self.dataset, df_transform)
        return {'transformed-data': df}

    def assign_transform(self):
        """Assigns appropriate transformation based on skewness and kurtosis."""
        df = self.raw_data_skew_kurt
        df = df.rename(columns={0: "skewness", 1: "kurtosis"})

        # Identify features containing negative values
        features_with_negatives = [
            col for col in self.dataset.columns
            if (self.dataset[col] < 0).any()]

        conditions = [
            (  # Box-Cox only for positive features
                (df["skewness"] > self.boxcox_skew_threshold) &
                (df["kurtosis"] > self.kurtosis_threshold) &
                (~df.index.isin(features_with_negatives))
            ),

            (  # Yeo-Johnson for skewed negative or mixed-sign features
                (df["skewness"] > self.yeo_johnson_skew_threshold) &
                (df.index.isin(features_with_negatives))
            ),

            # Log transformation for moderate skewness
            (df["skewness"] > self.log_skew_threshold) & (~df.index.isin(features_with_negatives))
        ]

        choices = ["box-cox", "yeo-johnson", "log"]
        df["transform"] = np.select(conditions, choices, default=None)
        return df

    def apply_transform(self, df, transform_mapping):
        """Applies transformations based on the assigned mapping."""
        for feature, row in transform_mapping.iterrows():
            if feature == self.config.target_col:
                continue

            trans = row["transform"]
            if trans is None:
                continue

            if trans == "log":
                df[feature] = np.log(df[feature] - df[feature].min() + 1)

            elif trans == "box-cox":
                transformed, _ = boxcox(df[feature] + 1e-6)
                df[feature] = transformed

            elif trans == "yeo-johnson":
                transformed, _ = yeojohnson(df[feature])  # Yeo-Johnson for negatives
                df[feature] = transformed

        return df
