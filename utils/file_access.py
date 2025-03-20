from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


class FileAccess:
    """Automatic file loading and saving."""
    @staticmethod
    def extract_suffix(path: Path):
        return path.suffix

    @staticmethod
    def load_file(path: Path):
        path = Path(path)
        suffix = path.suffix
        logging.getLogger("file_access").file_track(f"Loading Input File: ``{path}``")
        if suffix == ".parquet":
            return pd.read_parquet(path)
        elif suffix == ".csv":
            return pd.read_csv(path)
        elif suffix == ".xlsx":
            return pd.read_excel(path)
        elif suffix == ".npy":
            return np.load(path)
        elif suffix == ".joblib":
            return joblib.load(path)
        elif suffix == ".json":
            return pd.read_json(path, orient="index")
        elif suffix == ".pdf":
            pass
        else:
            raise ValueError(f"Unknown file type: {suffix}")

    @staticmethod
    def save_file(df: pd.DataFrame, path: Path, index=False):
        suffix = path.suffix
        logging.getLogger("file_access").file_track(f"Saving Output File: ``{path}``")
        if suffix == ".parquet":
            return df.to_parquet(path, index=index)
        elif suffix == ".csv":
            return df.to_csv(path, index=index)
        elif suffix == ".xlsx":
            return df.to_excel(path, index=index)
        elif suffix == ".npy":
            return np.save(path, df)
        elif suffix == ".joblib":
            return joblib.dump(df, path)
        elif suffix == ".json":
            if isinstance(df, pd.DataFrame):
                return df.to_json(path, orient="records", indent=4)
            elif isinstance(df, dict):
                return FileAccess.save_json(df, path)
        elif suffix == ".txt":
            with open(path, "a", encoding="utf-8") as f:
                f.write(df)
        else:
            raise ValueError(f"Unknown file type: {path} {suffix}")

    @staticmethod
    def load_json(path):
        with open(path, "r") as file:
            return json.load(file)

    @staticmethod
    def save_json(data, path, overwrite=False):
        if overwrite is False and Path(path).exists():
            pass
        else:
            logging.debug(f"Saving json to ``{path}``")
            with open(path, "w") as file:
                json.dump(data, file)
