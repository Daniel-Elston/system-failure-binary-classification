from __future__ import annotations

from pathlib import Path

from config.pipeline_context import PipelineContext
from config.states import DataState
from utils.file_access import FileAccess
from typing import Optional

class DataModule:
    def __init__(
        self, ctx: PipelineContext,
        state_key: str = None,
        data_path: Path = None,
        data_dict: Optional[dict] = None,
    ):
        """
        _summary_
        ----------
        Class to handle data storage, with optional data dictionary transformations applied.
        
        _extended_summary_
        ----------
            - Load data from either in-memory state or a local file.
            - Save data to either in-memory state or a local file.
            - Apply data dictionary transformations if provided.    
        
        Outputs
        ----------
            - Data accessible from in-memory state or local file (optionally transformed).
        
        Parameters
        ----------
        ctx : PipelineContext
            _description_
        state_key : str, optional
            _description_, by default None
        data_path : Path, optional
            _description_, by default None
        data_dict : dict, optional
            _description_, by default None
        
        Raises
        ------
        ValueError
            _description_
        """        

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
            data = self.load_from_state()
        elif self.data_path and self.data_path.exists():
            data = self.load_from_file()
        else:
            raise ValueError(
                f"Unable to load data. `state_key`: {self.state_key}, `data_path`: {self.data_path}"
            )
        data = self.apply_data_dict(data)
        return data

    def save(self, data):
        """Save data either to the in-memory state or a local file"""
        if self.state_key:
            self.save_to_state(data)
        elif self.data_path:
            self.save_to_file(data)
        else:
            raise ValueError(
                f"Unable to save data. `state_key`: {self.state_key}, `data_path`: {self.data_path}"
            )

    def load_from_file(self):
        return FileAccess.load_file(self.data_path)

    def save_to_file(self, data):
        FileAccess.save_file(data, self.data_path)

    def load_from_state(self):
        return self.data_state.get(self.state_key)

    def save_to_state(self, data):
        self.data_state.set(self.state_key, data)

    def apply_data_dict(self, df):
        """Apply data dictionary transformations in the correct order"""
        if not self.dd:
            return df
        transforms = self.dd.transforms_store()
        for func_name, func in transforms.items():
            df = func(df)
        return df
