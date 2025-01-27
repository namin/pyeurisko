"""H5 heuristic implementation: Choose multiple slots to specialize."""
from typing import Any, Dict, List
import random
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h5(heuristic) -> None:
    """Configure H5: Choose multiple slots to randomly specialize."""
    heuristic.set_prop('worth', 151)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN randomly select which slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular slots of u to specialize")
    heuristic.set_prop('arity', 1)
    heuristic.set_prop('subsumes', ['h3'])
    heuristic.set_prop('subsumed_by', ['h5-criterial', 'h5-good'])

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we need to choose slots to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            logger.debug("No unit or task")
            return False
            
        # Check task type and missing slot selection
        is_specialization = task.get('task_type') == 'specialization'
        logger.debug(f"H5 task type is {task.get('task_type')}, checking specialization")
        no_slots_chosen = 'slot_to_change' not in task
        logger.debug(f"H5 no slots chosen: {no_slots_chosen}")
        
        if not (is_specialization and no_slots_chosen):
            return False
        
        # Check agenda count as in LISP
        task_manager = rule.task_manager
        if task_manager:
            similar_tasks = sum(1 for t in task_manager.agenda
                              if (t.get('unit') == unit.name and 
                                  t.get('task_type') == 'specialization'))
            if similar_tasks >= 7:  # LISP used 7 as threshold
                logger.debug("Too many similar tasks")
                return False
                
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of slot choices."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        slots = task.get('slots_to_change', [])
        if not slots:
            return False
            
        logger.info(f"\n{unit.name} will be specialized by specializing the following "
                   f"of its slots: {slots}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Randomly select slots for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False

        # Focus on non-function slots that can be specialized
        slot_keys = ['domain', 'range', 'isa', 'applics', 'applications']
        logger.debug(f"Getting slots for {unit.name}")
        valid_slots = []
        for key in slot_keys:
            if unit.has_prop(key) and unit.get_prop(key) is not None:
                valid_slots.append(key)
                
        logger.debug(f"Valid slots after filtering: {valid_slots}")

        if not valid_slots:
            return False

        # Select multiple slots randomly
        num_slots = min(random.randint(1, 3), len(valid_slots))
        selected_slots = random.sample(valid_slots, num_slots)
        
        if not selected_slots:
            return False
            
        # Update task
        task['slots_to_change'] = selected_slots 
        task['credit_to'] = task.get('credit_to', []) + ['h5']
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add specialization tasks for chosen slots."""
        unit = context.get('unit')
        task = context.get('task')
        task_manager = rule.task_manager
        
        if not all([unit, task, task_manager]):
            return False
            
        selected_slots = task.get('slots_to_change', [])
        if not selected_slots:
            return False

        base_priority = task.get('priority', 500)
        
        tasks_added = 0
        for slot in selected_slots:
            # Create specialized task
            new_task = {
                'priority': int((base_priority + rule.worth_value() + 
                              unit.worth_value()) / 3),
                'unit': unit.name,
                'slot': 'specializations',
                'reasons': [f"A new unit will be created by specializing the {slot} "
                          f"slot of {unit.name}; that slot was chosen randomly."],
                'task_type': 'specialization',
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h5'] + task.get('credit_to', [])
                }
            }
            task_manager.add_task(new_task)
            tasks_added += 1
            
        if tasks_added == 0:
            return False
            
        # Record task creation
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"{len(selected_slots)} specific slots of {unit.name} to find specializations of"
        ]
        context['task_results'] = task_results
            
        return True