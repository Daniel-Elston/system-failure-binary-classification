from __future__ import annotations

from typing import Any
from typing import Dict

import pandas as pd

from config.pipeline_context import PipelineContext
from src.core.data_handling.data_dict import RawDataDict
from src.core.data_handling.data_module import DataModule


module_map: Dict[str, dict] = {
    "raw-data": RawDataDict(),
}


class DataModuleHandler:
    """
    Summary
    ----------
    DataModule instance manager
    Factory and cache for DataModule instances with path-based lookup.

    Extended Summary
    ----------
    - Maintains mapping between path keys and DataModule configurations
    - Caches DataModule instances for reuse
    - Coordinates bulk save operations
    - Implements error handling for data operations

    Outputs
    ----------
    Initialized handler ready for data operations

    Parameters
    ----------
    ctx : PipelineContext
        Contains path configurations and runtime state
    """

    def __init__(
        self, ctx: PipelineContext
    ):
        self.ctx = ctx
        self.modules: Dict[str, DataModule] = {}
        self.module_map: Dict[str, dict] = module_map

    def get_dm(self, path_key: str) -> DataModule:
        """
        Retrieves DataModule instance
        Implements caching to avoid redundant initialisations.
        """
        data_dict = self.module_map.get(path_key)
        dm = DataModule(
            self.ctx,
            data_path=self.ctx.paths.get_path(path_key),
            data_dict=data_dict
        )
        if path_key not in self.modules:
            self.modules[path_key] = dm
        return self.modules[path_key]

    def save_data(self, path_data_pair: Dict[str, pd.DataFrame]):
        """Handles multiple data persistence operations in single call."""
        try:
            for path_key, data in path_data_pair.items():
                dm = self.get_dm(path_key)
                return dm.save(data)
        except TypeError:
            raise TypeError(f"Unsupported data type: {type(data)} for path: {path_key}")

    def load_dm(self, dm: DataModule) -> Any:
        """Safe load data from a specified DataModule."""
        if dm is None:
            raise AttributeError('NoneType: Verify module path keys, and path config keys')
        try:
            if not hasattr(dm, "_loaded_data"):
                dm._loaded_data = dm.load()
                if dm._loaded_data is None:
                    raise ValueError(f"Dataset at {dm.data_path} is empty.")
            return dm._loaded_data
        except Exception as e:
            raise ValueError(f"Failed to load data from {dm.data_path}: {e}")
