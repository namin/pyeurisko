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
    logger.info("H3 checking if_potentially_relevant")
    #logger.info(f"Rule: {rule}, Context: {context}")
        
    task = context.get('task')
    if not task:
        logger.info("No task in context")
        return False
            
    logger.info(f"Task type: {task.task_type}")
    return task.task_type == 'specialization'

def check_then_compute(rule, context):
    """Choose slots that could be specialized."""
    logger.info("Starting h3 then_compute")
    #logger.info(f"Rule: {rule}, Context: {context}")
    logger.info(f"Rule properties: {rule.properties if hasattr(rule, 'properties') else 'No properties'}")
        
    unit = context.get('unit')
    if not unit:
        logger.info("No unit in context")
        return False
            
    # Find slots with non-empty values that could be specialized
    candidate_slots = []
    for slot in SPECIALIZABLE_SLOTS:
        logger.info(f"Checking slot: {slot}")
        if unit.has_prop(slot):
            value = unit.get_prop(slot)
            logger.info(f"Found value for {slot}: {value}")
            if value is not None and value != []:
                candidate_slots.append(slot)
                logger.info(f"Added {slot} to candidate slots")
            else:
                logger.info(f"Rejected {slot} - empty value")
        else:
            logger.info(f"Unit does not have slot {slot}")
                    
    if not candidate_slots:
        logger.info("No candidate slots found")
        return False

    # Store candidate slots for then_add_to_agenda  
    context['candidate_slots'] = candidate_slots
    logger.info(f"Found candidate slots: {candidate_slots}")
    
    # Create or initialize task_results
    task_results = context.get('task_results', {})
    if not task_results:
        task_results = {
            'status': 'in_progress',
            'new_tasks': [],
            'success': True
        }
        context['task_results'] = task_results

    logger.info(f"Task results after compute: {task_results}")
    return True

def check_then_add_to_agenda(rule, context):
    """Create specialization tasks for chosen slots."""
    logger.info("H3 then_add_to_agenda starting")
    logger.info(f"Context: {context}")

    # Get needed context items
    unit = context.get('unit')
    task = context.get('task')
    candidate_slots = context.get('candidate_slots')
    
    if not all([unit, task, candidate_slots]):
        logger.info(f"Missing required context: unit={unit}, task={task}, candidate_slots={candidate_slots}")
        return False
        
    # Create a specialization task for each candidate slot
    new_tasks = []
    for slot in candidate_slots:
        new_task = Task(
            priority=task.priority - 10,  # Slightly lower priority but not too much
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
        logger.info(f"Created new task for slot {slot} with supplemental {new_task.supplemental}")
           
    # Store results directly in context
    context['task_results'] = {
        'status': 'completed',
        'success': True,
        'new_tasks': new_tasks
    }
    logger.info(f"Final task results with {len(new_tasks)} new tasks: {context['task_results']}")
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
