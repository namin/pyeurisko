from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from .unit import Unit, UnitRegistry

@dataclass
class Task:
    """Represents a task to be worked on by the system."""
    priority: int
    unit_name: str
    slot_name: str
    reasons: List[str]
    supplemental: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: 'Task') -> bool:
        """Tasks are ordered by priority, higher priority first."""
        return self.priority > other.priority  # Reversed for priority queue

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

    def work_on_task(self, task: Task, interpreter: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a task using the provided interpreter."""
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
            'supplemental': task.supplemental,
        }

        # Execute pre-task heuristics
        if not self._execute_task_phase(unit, 'if_about_to_work_on_task', context):
            return {'status': 'aborted', 'phase': 'pre-task'}

        # Execute main task work
        if interpreter:
            success = interpreter(unit, context)
            if not success:
                return {'status': 'failed', 'phase': 'main'}

        # Execute post-task heuristics
        if not self._execute_task_phase(unit, 'if_finished_working_on_task', context):
            return {'status': 'aborted', 'phase': 'post-task'}

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
