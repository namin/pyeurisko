"""H6 heuristic implementation: Specialize a chosen slot."""
import random
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def specialize_value(value):
    """Create a specialized version of a value."""
    if isinstance(value, list):
        if len(value) <= 1:
            return None
        # Take a subset
        n = max(1, len(value) - 1)
        return value[:n]
        
    elif isinstance(value, str):
        if value in ['anything', 'op', 'math-op', 'num-op', 'binary-op']:
            # For ISA hierarchies, remove later/more specific terms
            return ['anything']
        return value
        
    elif isinstance(value, (int, float)):
        return int(value * 0.9)  # Reduce value by 10%
        
    return None

def init_task_results(context):
    """Initialize task results structure if needed."""
    if 'task_results' not in context:
        context['task_results'] = {
            'status': 'in_progress',
            'initial_unit_state': {},
            'new_units': [],
            'new_tasks': [],
            'modified_units': []
        }
    else:
        results = context['task_results']
        if 'new_units' not in results:
            results['new_units'] = []
        if 'new_tasks' not in results:
            results['new_tasks'] = []
        if 'modified_units' not in results:
            results['modified_units'] = []
    return context['task_results']

def setup_h6(heuristic):
    """Configure H6 to specialize chosen slots."""
    heuristic.set_prop('worth', 700)  # From original Eurisko
    heuristic.set_prop('english',
        "IF the current task is to specialize a unit, and a slot has been chosen to be "
        "the one changed, THEN randomly select a part of it and specialize that part")
    heuristic.set_prop('abbrev', "Specialize a given slot of a given unit")
    heuristic.set_prop('arity', 1)

    @rule_factory  
    def if_potentially_relevant(rule, context):
        """Check that this is a specialization task with a chosen slot."""
        task = context.get('task')
        logger.debug(f"H6 task: {task}")

        if not task:
            logger.debug("H6: No task in context")
            return False
            
        logger.debug(f"H6 task type: {task.task_type}, supplemental: {task.supplemental}")

        # Must be a specialization task
        if task.task_type != 'specialization':
            logger.debug(f"H6: Wrong task type: {task.task_type}")
            return False
            
        # Must have slot_to_change in supplemental data
        slot_to_change = task.supplemental.get('slot_to_change')
        if not slot_to_change:
            logger.debug("H6 rejecting task: no slot_to_change in supplemental")
            return False
            
        logger.debug(f"H6 accepting task for slot: {slot_to_change}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Create specialized value."""
        logger.debug("H6 then_compute starting")
        
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            logger.debug("H6: Missing unit or task")
            return False
            
        # Get slot to specialize from task supplemental
        slot = task.supplemental.get('slot_to_change')
        if not slot or not unit.has_prop(slot):
            logger.debug(f"H6: Invalid slot to change: {slot}")
            return False
            
        # Get and store old value
        old_value = unit.get_prop(slot)
        if old_value is None:
            logger.debug("H6: No value to specialize")
            return False
            
        # Check if this slot/unit combination has been specialized before
        specialization_key = (unit.name, slot, str(old_value))
        unit.specialized_slots = getattr(unit, 'specialized_slots', set())
        if specialization_key in unit.specialized_slots:
            logger.debug("H6: Already specialized this slot/value combination")
            return False
            
        # Try specialization
        new_value = specialize_value(old_value)
        if new_value is None or new_value == old_value:
            logger.debug("H6: Could not create specialized value")
            return False
            
        # Record specialization
        unit.specialized_slots.add(specialization_key)
            
        # Store results
        logger.debug(f"H6: Specialized {slot} from {old_value} to {new_value}")
        context['old_value'] = old_value
        context['new_value'] = new_value
        context['slot_to_change'] = slot

        # Initialize task results
        init_task_results(context)
        return True

    @rule_factory  
    def then_define_new_concepts(rule, context):
        """Create new specialized unit."""
        logger.debug("H6 then_define_new_concepts starting")
        
        # Get required values
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        new_value = context.get('new_value')
        task_results = init_task_results(context)
        
        logger.debug(f"H6: Checking requirements - unit: {unit}, slot: {slot}, new_value: {new_value}")
        if not all([unit, slot, new_value is not None]):
            logger.debug("H6: Missing requirements for new unit")
            return False
        logger.debug("H6: All requirements present")

        # Get task manager
        task_manager = context.get('task_manager')
        logger.debug(f"H6: Got task manager: {task_manager}")
        if not task_manager:
            logger.debug("H6: No task manager in context")
            return False
            
        unit_registry = task_manager.unit_registry
        logger.debug(f"H6: Got unit registry: {unit_registry}")
        if not unit_registry:
            logger.debug("H6: No unit registry from task manager")
            return False
            
        # Create new specialized unit
        new_name = f"{unit.name}-{slot}-spec"
        logger.debug(f"H6: Creating new unit {new_name}")
        
        new_unit = unit_registry.create_unit(new_name)
        if not new_unit:
            logger.debug("H6: Failed to create new unit")
            return False
            
        # Copy properties except specialized slot and relationship slots
        for key, value in unit.properties.items():
            if key != slot and key not in ['specializations', 'generalizations']:
                new_unit.set_prop(key, value)
                
        # Set specialized value and reduced worth
        new_unit.set_prop(slot, new_value)
        new_unit.set_prop('worth', int(unit.worth_value() * 0.9))
        
        # Update unit relationships
        new_unit.set_prop('generalizations', [unit.name])
        if not unit.has_prop('specializations'):
            unit.set_prop('specializations', [])
        unit.add_to_prop('specializations', new_name)
        
        # Register new unit
        if not unit_registry.register(new_unit):
            logger.debug("H6: Failed to register new unit")
            return False
            
        # Mark success
        logger.debug(f"H6: Successfully created and registered unit {new_name}")
        
        # Add new unit to task results
        task_results['new_units'].append(new_unit)
        task_results['status'] = 'completed'
        task_results['success'] = True
        
        # Log final results
        logger.debug(f"H6: Final task results: {task_results}")
        logger.debug(f"H6: Final task results with new unit: {task_results}")
        return True

    # Set the functions as properties on the heuristic
    heuristic.set_prop('if_potentially_relevant', if_potentially_relevant)
    heuristic.set_prop('then_compute', then_compute)
    heuristic.set_prop('then_define_new_concepts', then_define_new_concepts)
