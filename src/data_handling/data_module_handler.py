from __future__ import annotations

import logging
from typing import Dict

import pandas as pd

from config.pipeline_context import PipelineContext
from src.data_handling.data_dict import RawDataDict
from src.data_handling.data_module import DataModule
from typing import Any


module_map: Dict[str, dict] = {
    "raw-data": RawDataDict(),
}


class DataModuleHandler:
    def __init__(
        self, ctx: PipelineContext
    ):
        """
        _summary_
        ----------
        Manages creates/retrieval of DataModules. Instantiates DataModules and allows interaction.
        
        _extended_summary_
        ----------
            - Load data from a specified DataModule.
            - Save data to a specified DataModule.
            - Get DataModule instance, or create it if it doesn't exist.
            - Create a DataModule instance.
            - Instantiate a DataModule and load data from it.
        
        Outputs
        ----------
            - Data accessible from DataModules.
            - Data saved to DataModules.
            - Instantiated DataModules.
        
        Parameters
        ----------
        ctx : PipelineContext
            _description_
        """        
        self.ctx = ctx
        self.modules: Dict[str, DataModule] = {}
        self.module_map: Dict[str, dict] = module_map

    def load_data(self, path_key: str):
        """Load data from a specified DataModule."""
        dm = self.get_or_create_data_module(path_key)
        return dm.load()

    def save_data(self, path_key: str, data: pd.DataFrame):
        """Save data to a specified DataModule."""
        try:
            dm = self.get_or_create_data_module(path_key)
            return dm.save(data)
        except TypeError:
            raise TypeError(f"Unsupported data type: {type(data)} for path: {path_key}")

    def get_or_create_data_module(self, path_key: str) -> DataModule:
        """Get DataModule instance, or create it if it doesn't exist."""
        if path_key not in self.modules:
            self.modules[path_key] = self._create_data_module(path_key)
        return self.modules[path_key]

    def _create_data_module(self, path_key: str) -> DataModule:
        """Create a DataModule instance."""
        data_dict = self.module_map.get(path_key)
        return DataModule(
            self.ctx,
            data_path=self.ctx.paths.get_path(path_key),
            data_dict=data_dict
        )

    def load_data_module(self, dm: DataModule) -> Any:
        if dm is None:
            raise AttributeError('NoneType: Verify module path keys, and path config keys')
        try:
            if not hasattr(dm, "_loaded_data"):
                dm._loaded_data = dm.load()
                if dm._loaded_data is None:
                    raise ValueError(f"Dataset at {dm.data_path} is empty.")
            return dm._loaded_data
        except Exception as e:
            raise ValueError(f"Failed to load data from {dm.data_path}: {e}", exc_info=True)
