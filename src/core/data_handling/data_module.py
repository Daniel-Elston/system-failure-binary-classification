from __future__ import annotations

from pathlib import Path
from typing import Optional

from config.pipeline_context import PipelineContext
from config.states import DataState
from utils.file_access import FileAccess


class DataModule:
    """
    Summary
    ----------
    Unified data access layer with transformation support
    Manages data persistence through multiple storage backends with optional
    data dictionary transformations.

    Extended Summary
    ----------
    - Provides transparent access to in-memory state or disk storage
    - Applies data quality transforms from data dictionary
    - Maintains consistency between runtime state and persisted data
    - Implements fallback logic for missing data sources

    Outputs
    ----------
    Initialized DataModule ready for load/save operations

    Parameters
    ----------
    ctx : PipelineContext
        Contains path configurations and runtime state
    state_key : str, optional
        Key for in-memory state storage, by default None
    data_path : Path, optional
        Filesystem path for disk storage, by default None
    data_dict : dict, optional
        Data quality transformations specification, by default None

    Raises
    ------
    ValueError
        If neither storage key is specified
    """

    def __init__(
        self, ctx: PipelineContext,
        state_key: str = None,
        data_path: Path = None,
        data_dict: Optional[dict] = None,
    ):
        if not state_key and not data_path:
            raise ValueError("Either `state_key` or `data_path` must be provided.")

        self.ctx = ctx
        self.state_key = state_key
        self.data_path = data_path
        self.dd = data_dict
        self.data_state: DataState = ctx.states.data

    def load(self):
        """Load data either from the in-memory state or a local file"""
        if self.state_key:
            data = self._load_from_state()
        elif self.data_path and self.data_path.exists():
            data = self._load_from_file()
        else:
            raise ValueError(
                f"Unable to load data. `state_key`: {self.state_key}, `data_path`: {self.data_path}"
            )
        data = self.apply_data_dict(data)
        return data

    def save(self, data):
        """Persists data to either in-memory state or disk"""
        if self.state_key:
            self._save_to_state(data)
        elif self.data_path:
            self._save_to_file(data)
        else:
            raise ValueError(
                f"Unable to save data. `state_key`: {self.state_key}, `data_path`: {self.data_path}"
            )

    def apply_data_dict(self, df):
        """Apply data dictionary transformations in the correct order"""
        if not self.dd:
            return df
        transforms = self.dd.transforms_store()
        for func_name, func in transforms.items():
            df = func(df)
        return df

    def _load_from_file(self):
        return FileAccess.load_file(self.data_path)

    def _save_to_file(self, data):
        FileAccess.save_file(data, self.data_path)

    def _load_from_state(self):
        return self.data_state.get(self.state_key)

    def _save_to_state(self, data):
        self.data_state.set(self.state_key, data)
