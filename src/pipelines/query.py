from __future__ import annotations

import logging

import pandas as pd

from config.paths import Paths
from config.pipeline_context import PipelineContext
from config.settings import Config
from src.data_handling.data_dict import NoDataDict
from src.data_handling.data_module import DataModule
from src.data_handling.data_module import load_dataset
from utils.execution import TaskExecutor


class QueryPipeline:
    """
    Pipeline to run any queries to inspect result1
    """

    def __init__(
        self, ctx: PipelineContext,
        exe: TaskExecutor,
    ):
        self.ctx = ctx
        self.exe = exe
        self.config: Config = ctx.settings.config
        self.paths: Paths = ctx.paths

        self.dd = NoDataDict()

        self.err_logs_full_dt = DataModule(
            data_path=self.paths.get_path("incorrect-exercises"),
            data_dict=self.dd,
        )
        self.uniq_err_logs = DataModule(
            data_path=self.paths.get_path("match-score-uniq-names-res"),
            data_dict=self.dd,
        )

    def __call__(self):
        """Identify name errors"""
        steps = [
            Querier(
                ctx=self.ctx,
                err_logs_uniq=load_dataset(self.uniq_err_logs),
                err_logs_full=load_dataset(self.err_logs_full_dt),
            )
        ]
        self.exe._execute_steps(steps, stage="parent")


class Querier:
    """Stores and runs quick queries"""

    def __init__(
        self, ctx: PipelineContext,
        err_logs_uniq: pd.DataFrame,
        err_logs_full: pd.DataFrame,
    ):
        self.ctx = ctx
        self.err_logs_uniq = err_logs_uniq
        self.err_logs_full = err_logs_full

        logging.warning(self.err_logs_full)
        print('\n')
        logging.warning(self.err_logs_uniq)
        print('\n')

    def __call__(self):
        self.run_queries()

    def run_queries(self):
        self.get_rows_by_incorrect_name(self.err_logs_full, 'exercise', 'cable v bar pulldown')
        # self.gets_rows_between_vc(self.err_logs_uniq, 0, 10)
        # self.queries()

    def get_rows_by_incorrect_name(self, dataset, col_name, name: str):
        """Return all rows where `incorrect_name` == `name`"""
        res = dataset.loc[dataset[col_name] == name]
        print(res[:50])
        print('\n')

    def queries(self, dataset):
        df = dataset[dataset['score_bin'].astype(str) == '1-10']
        print(df)
        print('\n')

    def gets_rows_between_vc(self, dataset, vc_min, vc_max):
        df = dataset[(dataset['val_count'] >= vc_min) & (dataset['val_count'] <= vc_max)]
        print(df)
        print('\n')
