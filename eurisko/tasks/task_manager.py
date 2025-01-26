"""Task manager."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from ..units import Unit, UnitRegistry
from ..slots import SlotRegistry
from .task import Task

logger = logging.getLogger(__name__)

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
        self.heuristic_stats = defaultdict(lambda: {'tries_for_success': 0, 'success': 0, 'tries_for_relevant': 0, 'relevant': 0})
        # Import here to avoid circular imports
        from ..system import System
        self.system = System(self)

    def _process_task_results(self, results: Dict[str, Any]) -> None:
        """Process task results to add new tasks."""
        if not results:
            return

        new_tasks = results.get('new_tasks', [])
        if isinstance(new_tasks, list):
            for task_info in new_tasks:
                if isinstance(task_info, dict):
                    task = Task(**task_info)
                    self.add_task(task)

    def _merge_task_priorities(self, existing: Task, new: Task) -> int:
        """Calculate merged task priority based on existing and new tasks."""
        base_priority = max(existing.priority, new.priority)
        # Consider task age and complexity
        reason_bonus = min(100, len(set(existing.reasons + new.reasons)) * 10)
        unit_bonus = 50 if self.unit_registry.get_unit(new.unit_name).worth_value() > 700 else 0
        return min(1000, base_priority + reason_bonus + unit_bonus)        

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
        # Add system to context
        context['system'] = self.system
        """Check if a heuristic's if-parts are satisfied."""
        logger.debug(f"\nChecking relevance of {heuristic.name}")
        logger.debug(f"Context: task_type={context.get('task_type')}, supplemental={context.get('supplemental')}")
        def check_factory_func(factory):
            """Handle function that returns another function."""
            if not factory:
                return True
                
            if not isinstance(factory, Callable):
                return True
                
            result = factory(heuristic, context)
            logger.debug(f"Factory result for {heuristic.name}: {result}")
            return result

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
        """Apply a heuristic's then-parts, assumes if_parts showed relevance."""

        # Ensure system is in context
        if 'system' not in context:
            context['system'] = self.system

        # Only proceed if relevant
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
        return success

    def track_heuristic_result(self, heuristic_name: str, mark: str, outcome: bool):
        stats = self.heuristic_stats[heuristic_name]
        tries_mark = 'tries_for_'+mark
        stats.setdefault(tries_mark, 0)
        stats.setdefault(mark, 0)
        stats[tries_mark] += 1
        if outcome:
            stats[mark] += 1

    def print_stats(self):
        print("\nHeuristic Performance:")
        for h_name, stats in sorted(self.heuristic_stats.items()):
            relevant_rate = (stats['relevant'] / stats['tries_for_relevant'] * 100) if stats['tries_for_relevant'] > 0 else 0
            success_rate = (stats['success'] / stats['tries_for_success'] * 100) if stats['tries_for_success'] > 0 else 0
            print(f"{h_name} -> {success_rate:.0f}% success ({relevant_rate:.0f}% relevant)")

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
            'system': self.system,
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
            logger.debug(f"Checking if {heuristic.name} relevant for task type {context.get('task_type')}")
            relevant = self._is_heuristic_relevant(heuristic, context)
            self.track_heuristic_result(heuristic.name, "relevant", relevant)
            if not relevant:
                logger.debug(f"{heuristic.name} not relevant")
                continue

            # Apply heuristic's then-parts
            logger.debug(f"Applying {heuristic.name}")
            success = self._apply_heuristic(heuristic, context)
            self.track_heuristic_result(heuristic.name, "success", success)

            if success and self.verbosity > 39:
                print(f"  The ThenParts of {heuristic.name} have been executed")

        # Update task results
        task.results.update({
            'status': 'completed',
            'old_value': current_value,
            'new_values': context['new_values'],
            'modified_unit': unit.properties  # Final state
        })

        self._process_task_results(task.results)
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

