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
    def if_potentially_relevant(rule, context):
        """Initial relevance check."""
        task = context.get('task')
        if not task:
            return False
            
        if task.get('task_type') != 'specialization':
            return False
            
        return True

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we need to choose slots to specialize."""
        unit = context.get('unit')
        task = context.get('task', {})
        if not unit or not task:
            logger.debug("H5: No unit or task")
            return False
            
        # Check task type and missing slot selection
        if not task.get('task_type') == 'specialization':
            logger.debug("H5: Not a specialization task")
            return False
            
        no_slots_chosen = 'slot_to_change' not in task.get('supplemental', {})
        logger.debug(f"H5 no slots chosen: {no_slots_chosen}")
        
        if not no_slots_chosen:
            logger.debug("H5: Slot already chosen")
            return False
        
        # Check agenda count as in LISP
        task_manager = rule.task_manager
        if task_manager:
            similar_tasks = sum(1 for t in task_manager.agenda
                              if (t.get('unit') == unit.name and 
                                  t.get('task_type') == 'specialization'))
            if similar_tasks >= 7:  # LISP used 7 as threshold
                logger.debug("H5: Too many similar tasks")
                return False
                
        logger.debug("H5: Task eligible for specialization")
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of slot choices."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            logger.debug("H5 then_print_to_user: Missing unit or task")
            return False
            
        slots = task.get('slots_to_change', [])
        if not slots:
            logger.debug("H5 then_print_to_user: No slots to change")
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
            logger.debug("H5 then_compute: Missing unit or task")
            return False

        logger.debug(f"H5 then_compute: Processing unit {unit.name}")
        logger.debug(f"H5 unit properties: {unit.properties}")

        # Get all slots that can be specialized
        specializable_slots = []
        for key, value in unit.properties.items():
            # Skip if value is None or empty
            if value is None or (isinstance(value, (list, dict)) and not value):
                continue
                
            # Skip special slots
            if key in ['creditors', 'worth', 'specializations', 'generalizations']:
                continue
                
            # Add slot if it's a list, dict, or primitive type
            if isinstance(value, (list, dict, str, int, float, bool)):
                specializable_slots.append(key)
                
        logger.debug(f"H5 specializable slots for {unit.name}: {specializable_slots}")

        if not specializable_slots:
            logger.debug("H5 then_compute: No specializable slots found")
            return False

        # Select multiple slots randomly with weighted probability
        # Prefer important slots like domain, range, isa
        weights = []
        important_slots = ['domain', 'range', 'isa', 'applics', 'applications']
        for slot in specializable_slots:
            weight = 3.0 if slot in important_slots else 1.0
            weights.append(weight)
            
        # Normalize weights
        total = sum(weights)
        weights = [w/total for w in weights]
        
        # Select 1-3 slots
        num_slots = min(random.randint(1, 3), len(specializable_slots))
        selected_slots = random.choices(specializable_slots, weights=weights, k=num_slots)
        selected_slots = list(set(selected_slots))  # Remove duplicates
        
        if not selected_slots:
            logger.debug("H5 then_compute: No slots selected")
            return False
            
        logger.debug(f"H5 selected slots: {selected_slots}")
            
        # Update task supplemental
        task['supplemental'] = task.get('supplemental', {})
        task['supplemental']['slots_to_change'] = selected_slots 
        task['supplemental']['credit_to'] = task['supplemental'].get('credit_to', []) + ['h5']
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add specialization tasks for chosen slots."""
        unit = context.get('unit')
        task = context.get('task')
        task_manager = rule.task_manager
        
        if not all([unit, task, task_manager]):
            logger.debug("H5 then_add_to_agenda: Missing required components")
            return False
            
        selected_slots = task.get('supplemental', {}).get('slots_to_change', [])
        if not selected_slots:
            logger.debug("H5 then_add_to_agenda: No slots selected")
            return False

        base_priority = task.get('priority', 500)
        
        tasks_added = 0
        for slot in selected_slots:
            # Create specialized task
            logger.debug(f"H5 creating task to specialize slot {slot} of {unit.name}")
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
                    'credit_to': ['h5'] + task.get('supplemental', {}).get('credit_to', [])
                }
            }
            task_manager.add_task(new_task)
            tasks_added += 1
            
        if tasks_added == 0:
            logger.debug("H5 then_add_to_agenda: No tasks added")
            return False
            
        # Record task creation  
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"{len(selected_slots)} specific slots of {unit.name} to find specializations of"
        ]
        task_results['status'] = 'completed'
        task_results['success'] = True
        context['task_results'] = task_results
        
        logger.debug(f"H5 then_add_to_agenda: Added {tasks_added} tasks")    
        return True