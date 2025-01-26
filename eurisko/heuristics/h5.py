"""H5 heuristic implementation: Choose multiple slots to specialize."""
from typing import Any, Dict, List
import random
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h5(heuristic) -> None:
    """Configure H5: Choose multiple slots to randomly specialize."""
    logger.debug("Setting up H5")
    heuristic.set_prop('worth', 151)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN randomly select which slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular slots of u to specialize")
    heuristic.set_prop('arity', 1)
    heuristic.set_prop('subsumes', ['h3'])
    heuristic.set_prop('subsumed_by', ['h5-criterial', 'h5-good'])
    logger.debug("H5 setup complete")

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we need to choose slots to specialize."""
        logger.debug(f"H5 if_working_on_task called with task type {context.get('task_type')}")
        unit = context.get('unit')
        task = context.get('current_task')
        if not unit or not task:
            logger.debug("No unit or task")
            return False
            
        # Check task type and missing slot selection
        is_specialization = task.task_type == 'specialization'
        logger.debug(f"H5 task type is {task.task_type}, checking specialization")
        no_slots_chosen = 'slot_to_change' not in task.supplemental
        logger.debug(f"H5 no slots chosen: {no_slots_chosen}, supplemental: {task.supplemental}")
        
        logger.debug(f"H5 checking specialization {is_specialization} and no slots {no_slots_chosen} for task {task.task_type}")
        
        # Check agenda count as in LISP
        task_manager = rule.task_manager
        if task_manager:
            similar_tasks = sum(1 for t in task_manager.agenda
                              if (t.unit_name == unit.name and 
                                  t.task_type == 'specialization'))
            if similar_tasks >= 7:  # LISP used 7 as threshold
                logger.debug("Too many similar tasks")
                return False
                
        return is_specialization and no_slots_chosen

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of slot choices."""
        unit = context.get('unit')
        slots = context.get('slots_to_change', [])
        if not unit or not slots:
            return False
            
        logger.info(f"\n{unit.name} will be specialized by specializing the following "
                   f"of its slots: {slots}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Randomly select slots for specialization."""
        unit = context.get('unit')
        task = context.get('current_task')
        if not unit or not task:
            return False

        # Focus on non-function slots that can be specialized
        slot_keys = ['domain', 'range', 'isa', 'applics', 'applications']
        logger.debug(f"Getting slots for {unit.name}")
        valid_slots = [k for k in slot_keys if k in unit.properties and unit.properties[k] is not None]
        logger.debug(f"Valid slots after filtering: {valid_slots}")
        slots = valid_slots

        if not slots:
            return False

        # Select multiple slots randomly
        num_slots = min(random.randint(1, 3), len(slots))
        selected_slots = random.sample(slots, num_slots)
        
        # Update context and task
        task.supplemental['slots_to_change'] = selected_slots
        task.supplemental['credit_to'] = task.supplemental.get('credit_to', []) + ['h5']
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add specialization tasks for chosen slots."""
        unit = context.get('unit')
        selected_slots = task.supplemental.get('slots_to_change', [])
        task = context.get('current_task')
        task_manager = rule.task_manager
        
        if not all([unit, selected_slots, task, task_manager]):
            return False

        new_tasks = []
        base_priority = task.priority
        
        from ..tasks import Task
        for slot in selected_slots:
            # Create specialized task for each slot
            new_task = Task(
                priority=int((base_priority + rule.worth_value() + 
                           unit.worth_value()) / 3),
                unit_name=unit.name,
                slot_name='specializations',
                reasons=[f"A new unit will be created by specializing the {slot} "
                        f"slot of {unit.name}; that slot was chosen randomly."],
                task_type='specialization',
                supplemental={
                    'slot_to_change': slot,
                    'credit_to': ['h5'] + task.supplemental.get('credit_to', [])
                }
            )
            new_tasks.append(new_task)
            
        # Sort tasks by priority and add to manager
        for task in sorted(new_tasks, key=lambda x: x.priority, reverse=True):
            task_manager.add_task(task)
            
        # Record task creation
        task.results['new_tasks'] = [
            f"{len(selected_slots)} specific slots of {unit.name} to find specializations of"
        ]
            
        return True