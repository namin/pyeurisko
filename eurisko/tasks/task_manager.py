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
        # Enhanced stats tracking
        self.cycle_stats = defaultdict(int)  # Stats for current cycle
        self.total_stats = defaultdict(int)  # Cumulative stats
        self.task_type_stats = defaultdict(int)  # Stats by task type
        self.unit_creation_stats = defaultdict(list)  # Track unit creation details
        self.unit_modification_stats = defaultdict(list)  # Track unit modifications
        from ..system import System
        self.system = System(self)

    def _process_task_results(self, results: Dict[str, Any]) -> None:
        """Process task results to add new tasks."""
        if not results:
            logger.info("No results to process")
            return

        logger.info(f"Processing task results: {results}")
        new_tasks = results.get('new_tasks', [])
        if isinstance(new_tasks, list):
            for task_info in new_tasks:
                if isinstance(task_info, Task):  # Already a Task object
                    logger.info(f"Adding Task object directly: {task_info}")
                    self.add_task(task_info)
                elif isinstance(task_info, dict):  # Task info dict
                    logger.info(f"Creating new Task from dict: {task_info}")
                    task = Task(**task_info)
                    self.add_task(task)
                    
            logger.info(f"Added {len(new_tasks)} new tasks from results")
        else:
            logger.info(f"No new tasks in results: {results}")

    def _merge_task_priorities(self, existing: Task, new: Task) -> int:
        """Calculate merged task priority."""
        base_priority = max(existing.priority, new.priority)
        reason_bonus = min(100, len(set(existing.reasons + new.reasons)) * 10)
        unit_bonus = 50 if self.unit_registry.get_unit(new.unit_name).worth_value() > 700 else 0
        return min(1000, base_priority + reason_bonus + unit_bonus)        

    def add_task(self, task: Task) -> None:
        """Add a task to the agenda."""
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
        logger.info(f"Adding {len(tasks)} tasks to agenda")
        for task in tasks:
            logger.info(f"Task to add: {task}")
            self.add_task(task)
        logger.info(f"Current agenda size: {len(self.agenda)}")

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
        """Check if a heuristic is relevant for the current task."""
        task = context.get('task')
        logger.debug(f"\nChecking relevance of {heuristic.name}")
        logger.debug(f"Context: task_type={context.get('task_type')}, supplemental={context.get('supplemental')}")
        logger.debug(f"Task info: {task.task_type if task else 'No task'}, {task.supplemental if task else 'No supplemental'}")


        def check_factory_func(factory):
            if not factory:
                return False

            if not isinstance(factory, Callable):
                return False

            try:
                result = factory(heuristic, context)
                return result is True
            except Exception as e:
                logger.debug(f"Factory error for {heuristic.name}: {e}")
                return False

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
        if 'system' not in context:
            context['system'] = self.system

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
                if result is not True:
                    if self.verbosity > 1:
                        print(f"Action from {prop_name} failed for {heuristic.name}")
                    all_actions_succeeded = False
            except Exception as e:
                if self.verbosity > 1:
                    print(f"Error applying heuristic {heuristic.name}: {e}")
                all_actions_succeeded = False

        success = any_action_executed and all_actions_succeeded and (
            len(context['task_results'].get('new_units', [])) > 0 or
            len(context['task_results'].get('new_tasks', [])) > 0 or
            len(context['task_results'].get('modified_units', [])) > 0
        )
        return success

    def track_heuristic_result(self, heuristic_name: str, mark: str, outcome: bool):
        """Track heuristic execution stats."""
        stats = self.heuristic_stats[heuristic_name]
        tries_mark = 'tries_for_'+mark
        stats.setdefault(tries_mark, 0)
        stats.setdefault(mark, 0)
        stats[tries_mark] += 1
        if outcome:
            stats[mark] += 1

    def print_stats(self):
        """Print comprehensive system stats."""
        print("\nSystem Statistics:")
        print(f"Total tasks executed: {self.total_stats['tasks_executed']}")
        print(f"Total units created: {self.total_stats['units_created']}")
        print(f"Total units modified: {self.total_stats['units_modified']}")
        
        print("\nTask Type Distribution:")
        for task_type, count in sorted(self.task_type_stats.items()):
            print(f"{task_type}: {count} tasks")
        
        print("\nUnit Creation by Heuristic:")
        for h_name, creations in sorted(self.unit_creation_stats.items()):
            if creations:
                print(f"{h_name}: {len(creations)} units created")
                for unit_name, task_type in creations[-3:]:  # Show last 3 examples
                    print(f"  - {unit_name} (from {task_type} task)")
        
        print("\nHeuristic Performance:")
        for h_name, stats in sorted(self.heuristic_stats.items()):
            relevant_rate = (stats['relevant'] / stats['tries_for_relevant'] * 100) if stats['tries_for_relevant'] > 0 else 0
            success_rate = (stats['success'] / stats['tries_for_success'] * 100) if stats['tries_for_success'] > 0 else 0
            print(f"{h_name} -> {success_rate:.0f}% success ({relevant_rate:.0f}% relevant)")

    def work_on_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task using heuristics."""
        self.task_num += 1
        self.current_task = task
        self.cycle_stats['tasks_executed'] += 1
        self.total_stats['tasks_executed'] += 1
        self.task_type_stats[task.task_type] += 1
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
                    if isinstance(result, list):
                        task.results['new_units'].extend(result)
                    elif isinstance(result, dict):
                        task.results.update(result)

            except Exception as e:
                if self.verbosity > 0:
                    print(f"Error executing slot function: {e}")

        # Get current slot value 
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
            'task': task,
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

        # Get heuristics that could apply
        heuristics = self._get_heuristics()

        # Try each heuristic
        for heuristic in heuristics:
            if self.abort_current_task:
                task.results['status'] = 'aborted'
                return task.results

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
            
            # Track unit creation and modification
            if success:
                new_units = context['task_results'].get('new_units', [])
                if new_units:
                    self.cycle_stats['units_created'] += len(new_units)
                    self.total_stats['units_created'] += len(new_units)
                    self.unit_creation_stats[heuristic.name].extend(
                        [(unit.name, task.task_type) for unit in new_units]
                    )
                
                if context['task_results'].get('modified_units', []):
                    self.cycle_stats['units_modified'] += 1
                    self.total_stats['units_modified'] += 1
                    self.unit_modification_stats[heuristic.name].append(
                        (unit.name, task.task_type)
                    )

            if success:
                if self.verbosity > 39:
                    print(f"  The ThenParts of {heuristic.name} have been executed")
                    
                if context.get('task_results', {}).get('new_tasks'):
                    logger.debug(f"{heuristic.name} created {len(context['task_results']['new_tasks'])} new tasks")
                if context.get('task_results', {}).get('new_units'):
                    logger.debug(f"{heuristic.name} created {len(context['task_results']['new_units'])} new units")

        """Update task results and process."""
        task.results.update({
            'status': 'completed',
            'old_value': current_value,
            'new_values': context['new_values'],
            'modified_unit': unit.properties  # Final state
        })
        
        # Process results
        logger.info(f"Processing task results for task {task.unit_name}:{task.slot_name}")
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
                result = self.work_on_task(task)
                results.append(result)
        return results
