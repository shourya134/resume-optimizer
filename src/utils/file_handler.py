"""
File Handler Utilities

Utilities for reading and writing files.
"""

from pathlib import Path
from typing import Optional


def read_latex_file(file_path: str) -> str:
    """
    Read a LaTeX file and return its content.

    Args:
        file_path: Path to the LaTeX file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a .tex file
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != '.tex':
        raise ValueError(f"File must be a .tex file, got: {path.suffix}")

    return path.read_text(encoding='utf-8')


def write_latex_file(content: str, file_path: str, overwrite: bool = False) -> Path:
    """
    Write content to a LaTeX file.

    Args:
        content: LaTeX content to write
        file_path: Destination file path
        overwrite: Whether to overwrite existing files

    Returns:
        Path to the written file

    Raises:
        FileExistsError: If file exists and overwrite is False
    """
    path = Path(file_path)

    if path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {file_path}. Use overwrite=True to replace.")

    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write content
    path.write_text(content, encoding='utf-8')

    return path


def read_text_file(file_path: str) -> str:
    """
    Read a text file and return its content.

    Args:
        file_path: Path to the text file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text(encoding='utf-8')


def ensure_output_path(input_path: str, suffix: str = "_optimized") -> Path:
    """
    Generate an output file path based on input path.

    Args:
        input_path: Input file path
        suffix: Suffix to add before extension

    Returns:
        Output file path

    Example:
        ensure_output_path("resume.tex", "_optimized") -> "resume_optimized.tex"
    """
    path = Path(input_path)
    output_path = path.parent / f"{path.stem}{suffix}{path.suffix}"
    return output_path
