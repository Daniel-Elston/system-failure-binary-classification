from __future__ import annotations

import warnings
from pathlib import Path
from typing import Tuple

import dotenv
import yaml

from config.pipeline_context import PipelineContext
from utils.logging_config import setup_logging
warnings.filterwarnings("ignore")


def load_config(config_path: Path) -> dict:
    """Load and return the project configuration."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def initialise_project_configs(
    config_filename: str = "config/logging.yaml",
    env_filename: str = ".env",
    log_filename: str = None,
) -> Tuple[Path, dict, PipelineContext]:
    """
    Initialize the project environment, load configuration,
    set up logging, and create PipelineContext.
    """
    project_dir = Path(__file__).resolve().parents[1]

    # Load environment variables
    dotenv.load_dotenv(project_dir / env_filename)

    # Load configuration
    config_path = project_dir / config_filename
    project_config = load_config(config_path)

    # Set up logging
    log_filename = log_filename or f"{Path(__file__).stem}.log"
    setup_logging("MainPipeline", project_dir, log_filename, project_config)

    # Initialize Pipeline Context
    return PipelineContext()


# def init_project() -> Tuple[Path, dict, PipelineContext]:
#     """Set up project environment, configuration, logging, and StateManager."""
#     return initialise_project_configs()
