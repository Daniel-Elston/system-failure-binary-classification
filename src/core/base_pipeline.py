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
from src.core.data_handling.data_module_handler import DataModuleHandler


class BasePipeline(ABC):
    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx
        self.paths: Paths = ctx.paths
        self.config: Config = ctx.settings.config
        self.params: Params = ctx.settings.params
        self.hyperparams: HyperParams = ctx.settings.hyperparams
        self.states: States = ctx.states
        self.data_state: DataState = ctx.states.data
        self.model_state: ModelState = ctx.states.model
        self.dm_handler = DataModuleHandler(ctx)
