from __future__ import annotations

import logging

import pandas as pd

from config.pipeline_context import PipelineContext
from src.core.base_pipeline import BasePipeline
from src.data_handling.data_dict import RawDataDict
from src.data_handling.data_module import DataModule

pd.set_option("display.max_columns", None)


class ValidationChecks(BasePipeline):
    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
    ):
        """
        _summary_
        ----------
        Utilises DataDictionary to perform data checks on raw dataset

        _extended_summary_
        ----------
            - Check for unexpected nulls
            - Validate dtypes
            - Check for invalid placeholders

        Outputs
        ----------
            - Logs for each check

        Parameters
        ----------
        ctx : PipelineContext
            Nested configuration object
        """
        super().__init__(ctx)
        self.dataset = dataset
        self.expected_dtypes = RawDataDict().data.get('dtypes')

    def perform_data_checks(self):
        no_expect_nulls, numeric_cols, float_cols, int_cols, str_cols = self.col_groups()
        steps = [
            ("Check for unexpected nulls", self.test_no_unexpected_nulls(no_expect_nulls)),
            ("Dtype validation", self.test_dtypes(float_cols, int_cols, str_cols)),
            ("Invalid placeholder check", self.test_no_invalid_placeholders(numeric_cols))
        ]
        for step_name, step_result in steps:
            logging.debug(f"{step_name}: {step_result}")

    def col_groups(self):
        cols = self.dataset.columns
        no_expect_nulls = cols.difference(['opx_vol'])
        float_cols = []
        int_cols = []
        str_cols = []

        for col in cols:
            dtype = self.expected_dtypes[col]
            if dtype == float:
                float_cols.append(col)
            elif dtype == int:
                int_cols.append(col)
            elif dtype == str:
                str_cols.append(col)
            else:
                raise ValueError(f"Invalid dtype '{dtype}' for column '{col}'.")
        numeric_cols = float_cols + int_cols
        assert len(self.dataset.columns) == len(self.expected_dtypes), (
            f"Expected {len(self.dataset.columns)} columns. DataDict uses dtype length {len(self.expected_dtypes)}."
        )
        assert len(self.dataset.columns) == len(numeric_cols) + len(str_cols), (
            f"Numeric and non-numeric columns do not add up to total columns."
        )
        return no_expect_nulls, numeric_cols, float_cols, int_cols, str_cols

    def test_no_unexpected_nulls(self, no_expect_nulls):
        col_store = []
        for col in no_expect_nulls:
            if self.dataset[col].isnull().any():
                col_store.append(col)
        return "PASSED: No unexpected nulls" if not col_store else f"FAILED: Unexpected nulls found in columns {col_store}. Continuing..."

    def test_dtypes(self, float_cols, int_cols, str_cols):
        # Check for float type
        for col in float_cols:
            assert pd.api.types.is_float_dtype(
                self.dataset[col]
            ), f"Column '{col}' should be float, but is {self.dataset[col].dtype}."

        # Check for int type
        for col in int_cols:
            assert pd.api.types.is_integer_dtype(
                self.dataset[col]
            ), f"Column '{col}' should be int, but is {self.dataset[col].dtype}."

        # Check for object/string type
        for col in str_cols:
            assert pd.api.types.is_object_dtype(
                self.dataset[col]
            ), f"Column '{col}' should be str/object, but isn't."
        return "PASSED: Dtypes validated"

    def test_no_invalid_placeholders(self, numeric_cols):
        for col in numeric_cols:
            invalid_vals = self.dataset[col][self.dataset[col].apply(lambda x: isinstance(x, str))]
            assert invalid_vals.empty, (
                f"Invalid string entries found in numeric column '{col}': {invalid_vals.unique()}"
            )
        return "PASSED: No invalid placeholders found"
