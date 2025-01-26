import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from ..units import Unit, UnitRegistry
from ..slots import SlotRegistry

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a task to be worked on by the system."""
    priority: int
    unit_name: str
    slot_name: str
    reasons: List[str]
    supplemental: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    task_type: Optional[str] = None
    
    def __post_init__(self):
        """Set task_type from supplemental data if provided."""
        if not self.task_type and 'task_type' in self.supplemental:
            self.task_type = self.supplemental['task_type']

    def __lt__(self, other: 'Task') -> bool:
        """Tasks are ordered by priority, higher priority first."""
        return self.priority > other.priority  # Reversed for priority queue
        
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access to task properties."""
        try:
            if key == 'supplemental':
                return self.supplemental
            if key == 'task_type':
                return self.task_type or self.supplemental.get('task_type')
            if hasattr(self, key):
                return getattr(self, key)
            return self.supplemental[key]
        except (KeyError, AttributeError):
            raise KeyError(f"Task has no item '{key}'")
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a task property with a default value."""
        try:
            return self[key]
        except KeyError:
            return default
