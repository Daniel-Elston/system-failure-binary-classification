from __future__ import annotations

import attr

from config.paths import Paths
from config.settings import Settings
from config.states import States


@attr.s
class PipelineContext:
    """
    Attributes:
        paths: Paths
        settings: Settings
        states: States
    """
    paths: Paths = attr.ib(factory=Paths)
    settings: Settings = attr.ib(factory=Settings)
    states: States = attr.ib(factory=States)
