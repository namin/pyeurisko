"""Task classes for managing unit operations."""

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

class TaskManager:
    """Manages the agenda of tasks to be worked on."""
    def __init__(self):
        self.agenda: List[Task] = []
        self.task_num: int = 0
        self.min_priority: int = 150
        self.unit_registry = UnitRegistry()
        self.slot_registry = SlotRegistry()
        self.abort_current_task: bool = False
        self.current_task: Optional[Task] = None
        self.verbosity: int = 1
        self.heuristic_stats = defaultdict(lambda: {'tries': 0, 'successes': 0})
        
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
        heuristics = [self.unit_registry.get_unit(name) 
                for name in self.unit_registry.get_units_by_category('heuristic')]
        logger.debug(f"Got heuristics: {[h.name for h in heuristics]}")
        return heuristics

    def _is_heuristic_relevant(self, heuristic: Unit, context: Dict[str, Any]) -> bool:
        """Check if a heuristic's if-parts are satisfied."""
        def check_factory_func(factory):
            """Handle function that returns another function."""
            if not factory:
                return True
                
            if not isinstance(factory, Callable):
                return True
                
            return factory(heuristic, context)

        # Check if_potentially_relevant first
        if_factory = heuristic.get_prop('if_potentially_relevant')
        if if_factory and not check_factory_func(if_factory):
            return False

        # Then check if_truly_relevant 
        if_factory = heuristic.get_prop('if_truly_relevant')
        if if_factory and not check_factory_func(if_factory):
            return False

        return True
    
    def _apply_heuristic(self, heuristic: Unit, context: Dict[str, Any]) -> bool:
        """Apply a heuristic's then-parts."""
        any_action_executed = False
        all_actions_succeeded = True

        for prop_name in heuristic.properties:
            if not prop_name.startswith('then_'):
                continue

            action_factory = heuristic.get_prop(prop_name)
            if not action_factory:
                continue
                
            if not isinstance(action_factory, Callable):
                if self.verbosity > 1:
                    print(f"Action from {prop_name} failed for {heuristic.name}")
                continue

            any_action_executed = True
            try:
                result = action_factory(heuristic, context)
                if not isinstance(result, bool) or not result:
                    if self.verbosity > 1:
                        print(f"Action from {prop_name} failed for {heuristic.name}")
                        all_actions_succeeded = False
            except Exception as e:
                if self.verbosity > 1:
                    print(f"Error applying heuristic {heuristic.name}: {e}")
                    all_actions_succeeded = False

        # Only count as success if at least one action executed and all executed actions succeeded
        success = any_action_executed and all_actions_succeeded
        self.track_heuristic_result(heuristic.name, success)
        return success

    def track_heuristic_result(self, heuristic_name: str, success: bool):
        """Track success/failure statistics for heuristics."""
        stats = self.heuristic_stats[heuristic_name]
        stats['tries'] += 1
        if success:
            stats['successes'] += 1

    def work_on_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task using heuristics."""
        self.task_num += 1
        self.current_task = task
        unit = self.unit_registry.get_unit(task.unit_name)

        if not unit:
            return {'status': 'failed', 'reason': 'unit not found'}

        # Get slot if it exists
        slot = self.slot_registry.get_slot(task.slot_name)
            
        # Reset task state
        self.abort_current_task = False
        task.results = {
            'status': 'in_progress',
            'initial_unit_state': unit.properties.copy(),
            'new_units': [],
            'modified_units': []
        }
        
        # Execute slot function if it exists
        if slot and slot.get_prop('function'):
            try:
                slot_func = slot.get_prop('function')
                if self.verbosity > 10:
                    print(f"Executing {task.slot_name} function on {unit.name}")
                    
                result = slot_func(unit)
                if result:
                    # Track created/modified units
                    if isinstance(result, list):
                        task.results['new_units'].extend(result)
                    elif isinstance(result, dict):
                        task.results.update(result)
                        
                    if self.verbosity > 10:
                        print(f"Slot function created units: {result}")
            except Exception as e:
                if self.verbosity > 0:
                    print(f"Error executing slot function: {e}")

        # Get current slot value - critical for heuristics to compare before/after
        current_value = unit.get_prop(task.slot_name)

        # Set up initial context
        context = {
            'unit': unit,
            'slot': task.slot_name,
            'priority': task.priority,
            'reasons': task.reasons,
            'task_num': self.task_num,
            'task_type': task.task_type,
            'supplemental': task.supplemental,
            'task_manager': self,
            'current_unit': unit,
            'current_slot': task.slot_name,
            'old_value': current_value,
            'current_value': current_value,
            'new_values': [],
            'task_results': task.results
        }

        if self.verbosity > 1:
            logger.debug(f"Task Number {self.task_num}:")
            logger.debug(f"  Unit: {unit.name}")
            logger.debug(f"  Task type: {task.task_type}")
            logger.debug(f"  Supplemental: {task.supplemental}")
            logger.debug(f"  Unit properties: {unit.properties}")

        # Get heuristics that could apply (analogous to (heuristics) in Lisp)
        heuristics = self._get_heuristics()

        # Try each heuristic (like the LOOP in work-on-task Lisp)
        for heuristic in heuristics:
            if self.abort_current_task:
                task.results['status'] = 'aborted'
                return task.results

            # Only apply if relevant (via if-parts)
            if not self._is_heuristic_relevant(heuristic, context):
                continue

            # Apply heuristic's then-parts
            success = self._apply_heuristic(heuristic, context)
            self.track_heuristic_result(heuristic.name, success)

            if success and self.verbosity > 39:
                print(f"  The ThenParts of {heuristic.name} have been executed")

        # Update task results
        task.results.update({
            'status': 'completed',
            'old_value': current_value,
            'new_values': context['new_values'],
            'modified_unit': unit.properties  # Final state
        })

        return task.results

    def print_stats(self):
        if self.heuristic_stats:
            print("\nHeuristic Performance:")
            for h_name, stats in sorted(self.heuristic_stats.items()):
                success_rate = (stats['successes'] / stats['tries'] * 100) if stats['tries'] > 0 else 0
                print(f"{h_name} -> {success_rate:.0f}% ({stats['tries']} tries, {stats['successes']} successes)")

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

