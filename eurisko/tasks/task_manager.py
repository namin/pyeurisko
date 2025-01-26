"""Task management and execution."""
from queue import PriorityQueue
from typing import Dict, Any, Tuple
import logging
from .tasks import Task
from .units import UnitRegistry
from .heuristics import setup_heuristic

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages the creation and execution of tasks."""
    
    def __init__(self):
        """Initialize task manager with empty agenda."""
        self.agenda = PriorityQueue()
        self.unit_registry = UnitRegistry()
        self.heuristics = []
        
    def add_task(self, task: Task) -> None:
        """Add a task to the agenda."""
        # Higher priority should come first
        self.agenda.put((-task.priority, id(task), task))
        
    def add_task_for_unit(self, unit_name: str, slot_name: str,
                         priority: int = 500, supplemental: Dict = None,
                         reasons: list = None) -> None:
        """Create and add a task for a unit."""
        task = Task(
            priority=priority,
            unit_name=unit_name,
            slot_name=slot_name,
            supplemental=supplemental or {},
            reasons=reasons or []
        )
        self.add_task(task)
        
    def initialize_heuristic(self, name: str) -> None:
        """Initialize and add a heuristic to the manager."""
        print(f"Setting up {name}")
        heuristic = self.unit_registry.create_unit(name)
        setup_heuristic(name, heuristic)
        self.heuristics.append(heuristic)
        
    def execute_task(self, task: Task, stats: Dict[str, Tuple[int, int]]) -> bool:
        """Execute a task using available heuristics."""
        print(f"\nStarting task {task.id}: {task.unit_name}:{task.slot_name}")
        unit = self.unit_registry.get_unit(task.unit_name)
        if not unit:
            logger.error(f"Unit {task.unit_name} not found")
            return False
            
        # Prepare task context
        context = {
            'task_manager': self,
            'current_task': task,
            'current_unit': unit,
            'task_results': {
                'new_units': [],
                'new_tasks': []
            }
        }
        
        # Apply each heuristic
        for heuristic in self.heuristics:
            print(f"\nApplying heuristic {heuristic.name}")
            
            # Set context for rule execution
            for rule_name in ['if_working_on_task', 'then_compute', 'then_add_to_agenda', 
                            'then_print_to_user', 'then_define_new_concepts']:
                rule = heuristic.get_prop(rule_name)
                if rule:
                    rule.task_manager = self
                    
            # Get rules
            if_rule = heuristic.get_prop('if_working_on_task')()
            compute_rule = heuristic.get_prop('then_compute')()
            add_rule = heuristic.get_prop('then_add_to_agenda')()
            print_rule = heuristic.get_prop('then_print_to_user')()
            define_rule = heuristic.get_prop('then_define_new_concepts')()
            
            # Update statistics
            stats[heuristic.name] = stats.get(heuristic.name, (0, 0))
            tries, successes = stats[heuristic.name]
            tries += 1
            
            # Execute rules if conditions met
            if if_rule and if_rule(heuristic, context):
                success = True
                try:
                    if print_rule:
                        success &= print_rule(heuristic, context)
                    if compute_rule:
                        success &= compute_rule(heuristic, context)
                    if add_rule:
                        success &= add_rule(heuristic, context)
                    if define_rule:
                        success &= define_rule(heuristic, context)
                except Exception as e:
                    logger.error(f"Error executing {heuristic.name}: {e}")
                    success = False
                    
                if success:
                    successes += 1
                    
            stats[heuristic.name] = (tries, successes)
            
        return True