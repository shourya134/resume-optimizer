"""
Logging Utilities

Simple logging configuration for the application.
"""

import logging
import os
from pathlib import Path


def setup_logger(name: str, level: str) -> logging.Logger:
    """
    Set up and configure logger.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Create console handler if not already added
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, level.upper()))

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


def log_workflow_step(agent_name: str, message: str, level: str):
    """
    Log a workflow step.

    Args:
        agent_name: Name of the agent
        message: Log message
        level: Log level
    """
    logger = setup_logger(
        name="resume_optimizer",
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    log_func = getattr(logger, level.lower())
    log_func(f"[{agent_name}] {message}")
