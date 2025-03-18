from __future__ import annotations

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
        print(self.path_key)

    def run(self):
        self.metadata()
        self.output_metadata()
        # self.generate_report()

    def metadata(self):
        df = self.dataset
        file_path = self.paths.get_path(f"{self.path_key}-metadata")
        print(file_path)

        with open(file_path, "w") as f:
            f.write("Head of the dataset:\n")
            f.write(df.head().to_string() + "\n\n")

            f.write("Dataset Info:\n")
            df.info(buf=f)

            f.write("\n\nDataset Description:\n")
            f.write(round(df.describe(), 3).to_string() + "\n")
    
    def output_metadata(self):
        df = self.dataset
        print("Head of the dataset:\n")
        print(df.head())    

        print("\n\nDataset Info:\n")
        df.info()

        print("\n\nDataset Description:\n")
        print(round(df.describe(), 3))

    def generate_report(self):
        profile = ProfileReport(self.dataset, title='title')
        profile.to_file(self.paths.get_path(f'{self.path_key}_quality_report'))
