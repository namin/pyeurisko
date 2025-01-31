"""Chess pattern discovery system."""
from .minimal_patterns import MinimalPatternLearner
from .discover_minimal import process_puzzles

__all__ = ['MinimalPatternLearner', 'process_puzzles']
