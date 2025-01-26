"""Task classes for managing unit operations."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from ..units import Unit, UnitRegistry

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

class TaskManager:
    """Manages the agenda of tasks to be worked on."""
    def __init__(self):
        self.agenda: List[Task] = []
        self.task_num: int = 0
        self.min_priority: int = 150
        self.unit_registry = UnitRegistry()
        self.abort_current_task: bool = False
        self.current_task: Optional[Task] = None
        self.verbosity: int = 1
        
    def _merge_task_priorities(self, existing: Task, new: Task) -> int:
        """Calculate merged task priority based on existing and new tasks."""
        base_priority = max(existing.priority, new.priority)
        reason_bonus = max(10, 100 * len(set(existing.reasons + new.reasons)))
        return min(1000, base_priority + reason_bonus)

    def add_task(self, task: Task) -> None:
        """Add a task to the agenda if priority meets minimum threshold."""
        if task.priority < self.min_priority:
            return

        # Look for existing similar task
        for existing in self.agenda:
            if (existing.unit_name == task.unit_name and 
                existing.slot_name == task.slot_name):
                # Merge tasks
                existing.reasons = list(set(existing.reasons + task.reasons))
                existing.priority = self._merge_task_priorities(existing, task)
                # Re-sort agenda
                self.agenda.sort()
                return

        # Add new task
        self.agenda.append(task)
        self.agenda.sort()

    def add_tasks(self, tasks: List[Task]) -> None:
        """Add multiple tasks to the agenda."""
        for task in tasks:
            self.add_task(task)

    def next_task(self) -> Optional[Task]:
        """Get the next highest priority task."""
        return self.agenda.pop(0) if self.agenda else None

    def has_tasks(self) -> bool:
        """Check if there are tasks in the agenda."""
        return bool(self.agenda)

    def execute_if_parts(self, unit: Unit, context: Dict[str, Any]) -> bool:
        """Execute the if-parts of a unit's heuristic."""
        if_parts = unit.get_prop('if_parts') or []
        for if_part in if_parts:
            if callable(if_part):
                try:
                    if not if_part(context):
                        return False
                except Exception as e:
                    if self.verbosity > 1:
                        print(f"Error in if-part execution: {e}")
                    return False
        return True

    def execute_then_parts(self, unit: Unit, context: Dict[str, Any]) -> bool:
        """Execute the then-parts of a unit's heuristic."""
        then_parts = unit.get_prop('then_parts') or []
        success = True
        for then_part in then_parts:
            if callable(then_part):
                try:
                    result = then_part(context)
                    if not result:
                        success = False
                except Exception as e:
                    if self.verbosity > 1:
                        print(f"Error in then-part execution: {e}")
                    success = False
        return success

    def _get_heuristics(self) -> List[Unit]:
        """Get all heuristic units."""
        return [self.unit_registry.get_unit(name) 
                for name in self.unit_registry.get_units_by_category('heuristic')]
                
    def _is_heuristic_relevant(self, heuristic: Unit, context: Dict[str, Any]) -> bool:
        """Check if a heuristic's if-parts are satisfied."""
        # Check if_potentially_relevant first
        check = heuristic.get_prop('if_potentially_relevant')
        if check and not check(context):
            return False
                
        # Then check if_truly_relevant 
        check = heuristic.get_prop('if_truly_relevant')
        if check and not check(context):
            return False
                
        return True
        
    def _apply_heuristic(self, heuristic: Unit, context: Dict[str, Any]) -> bool:
        """Apply a heuristic's then-parts."""
        then_parts = []
        
        # Get all the then_ slots
        for prop_name in heuristic.properties:
            if prop_name.startswith('then_'):
                action = heuristic.get_prop(prop_name)
                if action:
                    if callable(action):
                        then_parts.append(action)
                    
        # Execute them
        success = True
        for action in then_parts:
            #try:
            if not action(context):
                success = False
            #except Exception as e:
            #    if self.verbosity > 1:
            #        print(f"Error applying heuristic {heuristic.name}: {e}")
            #    success = False
                
        return success
        
    def work_on_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task using available heuristics."""
        self.task_num += 1
        self.current_task = task
        unit = self.unit_registry.get_unit(task.unit_name)
        
        if not unit:
            return {'status': 'failed', 'reason': 'unit not found'}
            
        # Reset task state
        self.abort_current_task = False
        task.results = {}
        
        # Set up task context
        context = {
            'priority': task.priority,
            'unit': unit,
            'slot': task.slot_name,
            'reasons': task.reasons,
            'task_num': self.task_num,
            'task_type': task.task_type,
            'supplemental': task.supplemental,
            'task_manager': self,
        }
        
        # Get and filter heuristics
        heuristics = self._get_heuristics()
        relevant_heuristics = []
        
        for heuristic in heuristics:
            if self._is_heuristic_relevant(heuristic, context):
                relevant_heuristics.append(heuristic)
                
        # Apply each relevant heuristic
        for heuristic in relevant_heuristics:
            if self.abort_current_task:
                task.results['status'] = 'aborted'
                return task.results
                
            success = self._apply_heuristic(heuristic, context)
            if not success and self.verbosity > 0:
                print(f"Heuristic {heuristic.name} failed")
                
        task.results['status'] = 'completed'
        return task.results

    def _execute_task_phase(self, unit: Unit, phase: str, context: Dict[str, Any]) -> bool:
        """Execute a specific phase of task processing."""
        phase_heuristics = unit.get_prop(phase) or []
        for heuristic in phase_heuristics:
            if callable(heuristic):
                try:
                    if not heuristic(context):
                        return False
                except Exception as e:
                    if self.verbosity > 1:
                        print(f"Error in {phase} execution: {e}")
                    return False
            if self.abort_current_task:
                return False
        return True

    def abort_task(self) -> None:
        """Signal that the current task should be aborted."""
        self.abort_current_task = True

    def process_agenda(self, interpreter: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Process all tasks in the agenda."""
        results = []
        while self.has_tasks():
            task = self.next_task()
            if task:
                result = self.work_on_task(task, interpreter)
                results.append(result)
        return results

