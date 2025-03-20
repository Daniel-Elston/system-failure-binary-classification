from __future__ import annotations

import json
import logging
from pathlib import Path

from src.core.step_handling.step_registry import StepRegistry
from src.pipelines.steps.checks_steps import get_validation_checks_steps
from src.pipelines.steps.evaluation_steps import get_evaluation_steps
from src.pipelines.steps.exploration_steps import get_exploration_steps
from src.pipelines.steps.processing_steps import get_processing_steps
from src.pipelines.steps.training_steps import get_training_steps
from utils.file_access import FileAccess


def debug_steps():
    steps = StepRegistry.list_all_steps()
    json_output = json.dumps(steps, indent=4)
    path = Path("src/pipelines/steps/steps_metadata.json")
    logging.warning(f"\n{json_output}\nSaving Output File: ``{path}``")
    FileAccess.save_json(steps, path, overwrite=True)
