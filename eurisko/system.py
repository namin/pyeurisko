"""Core Eurisko system class."""
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class System:
    """Manages global Eurisko state and operations."""
    
    def __init__(self, task_manager=None):
        self.task_manager = task_manager
        self._name_counter = 0
        self.conjectures = []
        self._units = {}
        
    def new_name(self, prefix: str) -> str:
        """Generate a new unique name with given prefix."""
        self._name_counter += 1
        return f"{prefix}-{self._name_counter}"
        
    def create_unit(self, name: str, category: str) -> Optional['Unit']:
        """Create and register a new unit."""
        try:
            from .units import Unit
            unit = Unit(name)
            unit.set_prop('isa', [category])
            self._units[name] = unit
            return unit
        except Exception as e:
            logger.error(f"Error creating unit: {e}")
            return None
            
    def add_conjecture(self, conjecture: 'Unit') -> bool:
        """Add a conjecture to the system."""
        if not conjecture or not hasattr(conjecture, 'name'):
            return False
        self.conjectures.append(conjecture)
        return True
        
    def add_task_result(self, key: str, value: Any) -> None:
        """Add result to current task."""
        if self.task_manager and self.task_manager.current_task:
            results = self.task_manager.current_task.results
            if key == 'new_tasks':
                results.setdefault('new_tasks', []).append(value)
            else:
                results[key] = value