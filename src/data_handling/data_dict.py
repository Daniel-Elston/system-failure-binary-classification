from __future__ import annotations

import numpy as np
import pandas as pd


class ApplyDataDict:
    def __init__(self):
        """Children to overwrite self.data"""
        self.data = {
            "dtypes": {},
            "use_cols": [],
            "rename_mapping": {},
            "na_values": [],
        }

    def apply_rename_mapping(self, df):
        return df.rename(columns=self.data["rename_mapping"])

    def apply_dtypes(self, df):
        for col, dtype in self.data["dtypes"].items():
            if col in df.columns:
                if dtype == "datetime":
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                if dtype == float:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                if dtype == int:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                    if df[col].isna().any():
                        df[col] = df[col].astype("Int64")  # Nullable integer dtype
                    else:
                        df[col] = df[col].astype(int)
                if isinstance(dtype, str):
                    df[col] = df[col].astype(dtype)
        return df

    def apply_use_cols(self, df):
        if not self.data["use_cols"]:  # Check if 'use_cols' is empty or None
            use_cols = df.columns
        else:
            use_cols = [
                col for col in self.data["use_cols"]
                if col in df.columns
            ]
        return df[use_cols]

    def apply_na_values(self, df):
        for v in self.data.get("na_values", []):
            df = df.replace(v, np.nan)
        return df

    def transforms_store(self):
        """Dict of transforms applied in sequence"""
        return {
            "apply_rename_mapping": self.apply_rename_mapping,
            "apply_dtypes": self.apply_dtypes,
            "apply_use_cols": self.apply_use_cols,
            "apply_na_values": self.apply_na_values,
        }


class NoDataDict(ApplyDataDict):
    def __init__(self):
        super().__init__()
        self.data = {
            "rename_mapping": {},
            "dtypes": {},
            "use_cols": [],
            "na_values": [],
        }


class RawDataDict(ApplyDataDict):
    def __init__(self):
        super().__init__()
        self.data = {
            "rename_mapping": {
                'ComponentAge': 'comp_age',
                'MonthlyRunTime': 'monthly_run_time',
                'Location': 'loc',
                'FlowRate': 'flow_rate',
                'OPXVolume': 'opx_vol',
                'MaxOutputRate': 'max_output_rate',
                'Sensor1': 's1',
                'Sensor2': 's2',
                'Sensor3': 's3',
                'Sensor4': 's4',
                'Sensor5': 's5',
                'Sensor5.1': 's6',
                'DaysSinceMaintenance': 'days_since_maintenance',
                'Target': 'target'
            },
            "dtypes": {
                "comp_age": float,
                "monthly_run_time": float,
                "loc": str,
                "flow_rate": float,
                "opx_vol": int,
                "max_output_rate": int,

                "s1": float,
                "s2": float,
                "s3": float,
                "s4": float,
                "s5": float,
                "s6": float,

                "days_since_maintenance": float,
                "target": int
            },
            # "use_cols": [
            #     'comp_age',
            #     'monthly_run_time',
            #     'loc',
            #     'flow_rate',
            #     'opx_vol',
            #     'max_output_rate',
            #     's1',
            #     's2',
            #     's3',
            #     's4',
            #     's5',
            #     's6',
            #     'days_since_maintenance',
            #     'target'
            # ],
            "use_cols": [],
            "na_values": [],
        }
