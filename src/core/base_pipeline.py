from __future__ import annotations

from abc import ABC

from config.paths import Paths
from config.pipeline_context import PipelineContext
from config.settings import Config
from config.settings import HyperParams
from config.settings import Params
from config.states import DataState
from config.states import ModelState
from config.states import States
from src.data_handling.data_module_handler import DataModuleHandler
from src.core.pipeline_executor import PipelineExecutor
from typing import Any


class BasePipeline(ABC):
    def __init__(
        self, ctx: PipelineContext,
    ):
        self.ctx = ctx
        self.paths: Paths = ctx.paths
        self.config: Config = ctx.settings.config
        self.params: Params = ctx.settings.params
        self.hyperparams: HyperParams = ctx.settings.hyperparams
        self.states: States = ctx.states
        self.data_state: DataState = ctx.states.data
        self.model_state: ModelState = ctx.states.model

        self.executor = PipelineExecutor()
        self.data_module_handler = DataModuleHandler(ctx)

    def _execute_steps(self, steps, stage=None): # old needs to be removed
        """Delegated to PipelineExecutor."""
        self.executor.run_steps(steps, stage=stage)

    def create_data_module(self, path_key):
        """Delegated to DataModuleHandler."""
        return self.data_module_handler.get_or_create_data_module(path_key)

    def load_data_module(self, dm):
        """Delegated to DataModuleHandler."""
        return self.data_module_handler.load_data_module(dm)

    def save_data(self, path_data_pair: dict):
        """Delegated to DataModuleHandler."""
        try:
            for path_key, data in path_data_pair.items():
                self.data_module_handler.save_data(path_key, data)
        except Exception as e:
            raise f"Ensure data is a dict and path-key exists:\n{e}"
        
    def load_data(self, path_key):
        """Delegated to DataModuleHandler."""
        return self.data_module_handler.load_data(path_key)
