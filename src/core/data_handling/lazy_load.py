from __future__ import annotations

import attrs

from src.core.data_handling.data_module import DataModule
from src.core.data_handling.data_module_handler import DataModuleHandler


@attrs.define
class LazyLoad:
    """
    A lightweight marker/wrapper that says:
    "When the pipeline is dispatched, call `data_module_handler.load_data_module(data_module)`.
    Provide the result as the argument."
    """
    dm: DataModule

    def load(self, dm_handler: DataModuleHandler):
        if self.dm is None:
            raise AttributeError("`NoneType` object. Verify module path keys, and path config keys")
        try:
            return dm_handler.load_dm(self.dm)
        except Exception as e:
            raise ValueError(f"Failed to load data from {self.dm.data_path}: {e}")
