"""H3 heuristic implementation: Choose slots for specialization."""
import logging
from ..heuristics import rule_factory
from ..tasks import Task

logger = logging.getLogger(__name__)

def check_if_potentially_relevant(rule, context):
    """Check if this is a specialization task."""
    logger.debug("H3 checking if_potentially_relevant")
        
    task = context.get('task')
    if not task:
        logger.debug("No task in context")
        return False
            
    logger.debug(f"Task type: {task.task_type}")
    return task.task_type == 'specialization'

def check_then_compute(rule, context):
    """Choose slots that could be specialized."""
    logger.debug("Starting h3 then_compute")
    
    unit = context.get('unit')
    if not unit:
        logger.debug("No unit in context")
        return False

    # Check for task limit in agenda
    task_manager = context.get('task_manager')
    if task_manager:
        unit_name = unit.name
        existing_specialization_tasks = [
            t for t in task_manager.agenda 
            if t.unit_name == unit_name and t.task_type == 'specialization'
        ]
        if len(existing_specialization_tasks) >= 11:
            logger.debug(f"Too many specialization tasks for unit {unit_name}")
            return False

    # First check if unit has criterial slots
    candidate_slots = []
    used_slots = getattr(unit, 'specialized_slots', set())

    if unit.has_prop('criterial-slots'):
        criterial_slots = unit.get_prop('criterial-slots')
        for slot in criterial_slots:
            if (unit.name, slot) not in used_slots:
                if unit.has_prop(slot):
                    value = unit.get_prop(slot)
                    logger.debug(f"Found value for {slot}: {value}")
                    if value is not None and value != []:
                        candidate_slots.append(slot)
                        logger.debug(f"Added criterial slot {slot}")
    else:
        # Look at all slots with values except specialization tracking
        for slot in unit.properties.keys():
            if (unit.name, slot) not in used_slots:
                if slot not in ['specializations', 'generalizations', 'specialized_slots']:
                    value = unit.get_prop(slot)
                    logger.debug(f"Found value for {slot}: {value}")
                    if value is not None and value != []:
                        candidate_slots.append(slot)
                        logger.debug(f"Added slot {slot}")
                    else:
                        logger.debug(f"Rejected {slot} - empty value")
                        
    if not candidate_slots:
        logger.debug("No candidate slots found")
        return False

    # Store candidate slots for then_add_to_agenda  
    context['candidate_slots'] = candidate_slots
    logger.debug(f"Found candidate slots: {candidate_slots}")
    
    # Create or initialize task_results
    task_results = context.get('task_results', {})
    if not task_results:
        task_results = {
            'status': 'in_progress',
            'new_tasks': [],
            'success': True,
            'initial_unit_state': unit.properties.copy()
        }
        context['task_results'] = task_results

    return True

def check_then_add_to_agenda(rule, context):
    """Create specialization tasks for chosen slots."""
    logger.debug("H3 then_add_to_agenda starting")
    logger.debug(f"Context: {context}")

    # Get needed context items
    unit = context.get('unit')
    task = context.get('task')
    candidate_slots = context.get('candidate_slots')
    
    if not all([unit, task, candidate_slots]):
        logger.debug(f"Missing required context: unit={unit}, task={task}, candidate_slots={candidate_slots}")
        return False
        
    # Initialize task tracking if needed
    if not hasattr(unit, 'specialized_slots'):
        unit.specialized_slots = set()
        
    # Create a specialization task for each candidate slot
    new_tasks = []
    base_priority = task.priority if task else 1000
    
    for slot in candidate_slots:
        # Track that we're specializing this slot
        unit.specialized_slots.add((unit.name, slot))
        
        # Create task with degrading priority 
        priority = max(100, int(base_priority * 0.9))
        new_task = Task(
            priority=priority,
            unit_name=unit.name,
            slot_name=slot,
            task_type='specialization',
            reasons=[f'H3 selected {slot} for specialization'],
            supplemental={
                'task_type': 'specialization',
                'slot_to_change': slot
            }
        )
        new_tasks.append(new_task)
        logger.debug(f"Created new task for slot {slot} with supplemental {new_task.supplemental}")
           
    # Store results directly in context
    context['task_results'] = {
        'status': 'completed',
        'success': True,
        'new_tasks': new_tasks
    }
    logger.debug(f"Final task results with {len(new_tasks)} new tasks: {context['task_results']}")
    return True

def setup_h3(heuristic):
    """Configure H3 to identify slots for specialization."""
    heuristic.set_prop('worth', 101)  # From original Eurisko
    heuristic.set_prop('english',
        "IF the current task is to specialize a unit, but no specific slot to "
        "specialize is yet known, THEN choose one")
    heuristic.set_prop('abbrev', "Randomly choose a slot to specialize")
    heuristic.set_prop('arity', 1)

    # Set the check functions directly in properties
    heuristic.set_prop('if_potentially_relevant', check_if_potentially_relevant)
    heuristic.set_prop('then_compute', check_then_compute)
    heuristic.set_prop('then_add_to_agenda', check_then_add_to_agenda)
