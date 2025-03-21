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


step_sequence = [
    "checks",
    "exploration",
    "processing",
    "exploration",
    "training",
    "evaluation",
]

def debug_steps():
    steps_metadata = StepRegistry.list_all_steps()

    ordered_steps = []
    for idx, step in enumerate(step_sequence, start=1):
        step_metadata = steps_metadata.get(step, [])
        ordered_steps.append({
            "step": step,
            "step_n": idx,
            "metadata": step_metadata,
        })

    json_output = json.dumps(ordered_steps, indent=4)
    path = Path("src/pipelines/steps/steps_metadata.json")
    logging.warning(f"\n{json_output}\nSaving Output File: ``{path}``")
    FileAccess.save_json(ordered_steps, path, overwrite=True)
