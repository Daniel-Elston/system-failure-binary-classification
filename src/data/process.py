from __future__ import annotations

import logging

import seaborn as sns

from config.pipeline_context import PipelineContext
from config.settings import Config
from src.data_handling.data_module import DataModule
sns.set_style("darkgrid")


class DataPreprocessor:
    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
    ):
        self.ctx = ctx
        self.dataset = dataset
        self.config: Config = ctx.settings.config

        self.log_skew_threshold = self.config.log_skew_threshold
        self.kurtosis_threshold = self.config.kurtosis_threshold
        self.boxcox_skew_threshold = self.config.boxcox_skew_threshold

    def run(self):
        steps = [
            ('remove_duplicates', self.remove_duplicates),
            ('encode_cat_cols', self.encode_cat_cols),
            ('remove_nan_columns', self.remove_nan_columns),
            ('remove_nan_rows', self.remove_nan_rows),
        ]
        df = self.dataset
        for name, func in steps:
            logging.info(f"Processing: {name}")
            df = func(df)
        return {'processed-data': df}
        # self.module_handler.save_data("processed", df)

    def remove_duplicates(self, df):
        return df.drop_duplicates(keep='first')

    def encode_cat_cols(self, df):
        df['loc'] = df['loc'].astype('category').cat.codes
        return df

    def remove_nan_columns(self, df):
        return df.drop(columns=['opx_vol'])

    def remove_nan_rows(self, df):
        return df.dropna()
