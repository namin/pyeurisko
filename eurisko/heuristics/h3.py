"""H3 heuristic implementation: Choose slots for specialization."""
import logging
from ..heuristics import rule_factory
from ..tasks import Task

logger = logging.getLogger(__name__)

SPECIALIZABLE_SLOTS = [
    'domain', 'range', 'isa', 'generalizations', 'worth', 
    'fast-alg', 'iterative-alg', 'recursive-alg'
]

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
    #logger.debug(f"Rule: {rule}, Context: {context}")
    #logger.debug(f"Rule properties: {rule.properties if hasattr(rule, 'properties') else 'No properties'}")
        
    unit = context.get('unit')
    if not unit:
        logger.debug("No unit in context")
        return False
            
    # Find slots with non-empty values that could be specialized
    candidate_slots = []
    for slot in SPECIALIZABLE_SLOTS:
        logger.debug(f"Checking slot: {slot}")
        if unit.has_prop(slot):
            value = unit.get_prop(slot)
            logger.debug(f"Found value for {slot}: {value}")
            if value is not None and value != []:
                candidate_slots.append(slot)
                logger.debug(f"Added {slot} to candidate slots")
            else:
                logger.debug(f"Rejected {slot} - empty value")
        else:
            logger.debug(f"Unit does not have slot {slot}")
                    
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
            'success': True
        }
        context['task_results'] = task_results

    #logger.debug(f"Task results after compute: {task_results}")
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
        
    # Create a specialization task for each candidate slot
    new_tasks = []
    for slot in candidate_slots:
        new_task = Task(
            priority=1000,  # Set priority higher than examine tasks
            unit_name=unit.name,
            slot_name=slot,  # Use the actual slot we want to specialize
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
    heuristic.set_prop('worth', 600)
    heuristic.set_prop('english',
        "IF working on a specialization task, THEN identify slots that might "
        "be worth specializing and create tasks for H6 to do the specialization")
    heuristic.set_prop('abbrev', "Choose slots for specialization")
    heuristic.set_prop('arity', 1)

    # Set the check functions directly in properties
    heuristic.set_prop('if_potentially_relevant', check_if_potentially_relevant)
    heuristic.set_prop('then_compute', check_then_compute)
    heuristic.set_prop('then_add_to_agenda', check_then_add_to_agenda)
