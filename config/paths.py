from __future__ import annotations

import logging
from pathlib import Path
from pprint import pformat
from typing import Dict
from typing import Optional
from typing import Union

import attr


paths_store = {
    # Raw
    "raw-data": Path('data/raw/data1.csv'),
    # "raw": Path('data/raw/data1_sample.csv'),

    # Processed
    "processed-data": Path('data/processed/processed.csv'),
    "transformed-data": Path('data/processed/transformed.csv'),
    "feature-eng": Path('data/processed/feature_eng.csv'),

    # Raw EDA
    "raw-data-metadata": Path('reports/analysis/raw_metadata_log.txt'),
    "raw-data-skew-kurt": Path('reports/analysis/raw_skew_kurt.json'),
    "raw-quality-report": Path('reports/analysis/raw_profiling_report.html'),

    # processed EDA
    "transformed-data-metadata": Path('reports/analysis/processed_metadata_log.txt'),
    "transformed-data-skew-kurt": Path('reports/analysis/processed_skew_kurt.json'),
    "transformed-data-quality-report": Path('reports/analysis/processed_profiling_report.html'),

    # Model data
    "selected-features": Path('data/model/selected_features.npy'),
    "x-train-selected": Path('data/model/x_train_selected.csv'),
    "x-test-selected": Path('data/model/x_test_selected.csv'),
    "model": Path('models/model.joblib'),

    "x-train": Path('data/model/x_train.csv'),
    "x-test": Path('data/model/x_test.csv'),
    "y-train": Path('data/model/y_train.csv'),
    "y-test": Path('data/model/y_test.csv'),

    "y-test-pred": Path('data/model/y_test_pred.npy'),

    # Figures
    "raw_figures": Path('reports/analysis/'),
    "transformed_figures": Path('reports/processed_eda/'),
    "evaluation_figures": Path('reports/evaluation/'),
}


@attr.s
class Paths:
    paths: Dict[str, Path] = attr.ib(factory=dict)

    def __attrs_post_init__(self):
        self.paths = {k: Path(v) for k, v in paths_store.items()}
        logging.debug(f"PathsConfig:\n{pformat(self.paths)}\n")

    def get_path(self, key: Optional[Union[str, Path]]) -> Optional[Path]:
        if key is None:
            return None
        if isinstance(key, Path):
            return key
        return self.paths.get(key)
