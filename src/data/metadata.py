from __future__ import annotations

import logging

import pandas as pd
from ydata_profiling import ProfileReport

from config.paths import Paths
from config.pipeline_context import PipelineContext
from src.data_handling.data_module import DataModule
pd.set_option("display.max_columns", None)


class CollectMetadata:
    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
        path_key: str
    ):
        self.ctx = ctx
        self.dataset = dataset
        self.path_key = path_key
        self.paths: Paths = ctx.paths

    def run(self):
        self.metadata()
        self.output_metadata()
        # self.generate_report()

    def metadata(self):
        file_path = self.paths.get_path(f"{self.path_key}-metadata")

        with open(file_path, "w") as f:
            f.write("Head of the dataset:\n")
            f.write(self.dataset.head().to_string() + "\n\n")

            f.write("Dataset Info:\n")
            self.dataset.info(buf=f)

            f.write("\n\nDataset Description:\n")
            f.write(round(self.dataset.describe(), 3).to_string() + "\n")
    
    def output_metadata(self):
        logging.debug(f"Head of the dataset:\n{self.dataset.head()}")
        logging.debug(f"\n\nDataset Info:\n{self.dataset.info()}")
        logging.debug(f"\n\nDataset Description:\n{round(self.dataset.describe(), 3)}")

    def generate_report(self):
        profile = ProfileReport(self.dataset, title='title')
        profile.to_file(self.paths.get_path(f'{self.path_key}_quality_report'))
