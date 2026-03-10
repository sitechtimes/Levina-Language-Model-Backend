"""llm_aligner package bootstrap.

This module is intentionally lightweight and import-safe so it can be used
within a Django project without causing side-effects at import time.

Exports:
 - Config: a small dataclass holding common paths/flags used by the package
 - __version__: package version string

Keep heavy work (parsing, MFA invocation, stats) in separate modules.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging
import os
from typing import Optional

__all__ = ["Config", "__version__"]

__version__ = "0.1.0"


@dataclass
class Config:
	"""Configuration object for llm_aligner.

	Use Config.from_env() to construct from environment variables. Keep this
	small — modules that need more specific settings can extend or accept
	overrides.
	"""

	corpus_dir: Path = Path(os.getenv("LLM_ALIGNER_CORPUS_DIR", "training_data/corpus"))
	aligned_output: Path = Path(os.getenv("LLM_ALIGNER_ALIGNED_OUTPUT", "training_data/aligned_output"))
	output_jsonl_path: Path = Path(os.getenv("LLM_ALIGNER_OUTPUT_JSONL_PATH", "russian_dictionary_out.jsonl"))
	stressed_dictionary_path: Path = Path(os.getenv("LLM_ALIGNER_STRESSED_DICTIONARY_PATH", "russian_mfa_stressed_output_new.dict"))
	conda_bat: str = os.getenv("LLM_ALIGNER_CONDA_BAT", "conda")
	# Add more fields as needed; keep defaults reasonable for local/dev.

	@classmethod
	def from_env(cls) -> "Config":
		"""Create a Config from environment variables.

		This does not mutate environment or perform IO. Calling code may
		choose to call dotenv.load_dotenv() before this if desired.
		"""
		return cls(
			corpus_dir=Path(os.getenv("LLM_ALIGNER_CORPUS_DIR")),
			aligned_output=Path(os.getenv("LLM_ALIGNER_ALIGNED_OUTPUT")),
			output_jsonl_path=Path(os.getenv("LLM_ALIGNER_OUTPUT_JSONL_PATH")),
			stressed_dictionary_path=Path(os.getenv("LLM_ALIGNER_STRESSED_DICTIONARY_PATH")),
			conda_bat=os.getenv("LLM_ALIGNER_CONDA_BAT"),
		)


# convenience instance: callers can import and override if they like
DEFAULT_CONFIG = Config.from_env()

