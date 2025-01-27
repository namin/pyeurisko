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
        return f"{value}_specialized"
        
    elif isinstance(value, (int, float)):
        return int(value * 0.9)
        
    return None

def setup_h6(heuristic):
    """Configure H6 to specialize chosen slots."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to specialize a unit, and a slot has been chosen "
        "to be the one changed, THEN specialize that slot's value")
    heuristic.set_prop('abbrev', "Specialize a given slot of a given unit")
    heuristic.set_prop('arity', 1)

    # Add record functions that return True for success
    def then_compute_record(rule, context):
        return True
        
    def then_define_new_concepts_record(rule, context):
        return True
        
    def overall_record(rule, context):
        return True
        
    heuristic.set_prop('then_compute_record', then_compute_record)
    heuristic.set_prop('then_define_new_concepts_record', then_define_new_concepts_record)
    heuristic.set_prop('overall_record', overall_record)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check that this is a specialization task with chosen slot."""
        task = context.get('task')
        logger.info(f"H6 checking relevance with context: {context}")
        logger.info(f"H6 task: {task}")

        if not task:
            logger.info("H6: No task in context")
            return False
            
        logger.info(f"H6 task type: {task.task_type}, supplemental: {task.supplemental}")

        if task.task_type != 'specialization':
            logger.info(f"H6: Wrong task type: {task.task_type}")
            return False
            
        slot_to_change = task.supplemental.get('slot_to_change')
        logger.info(f"H6 checking task with supplemental: {task.supplemental}")
        if not slot_to_change:
            logger.info("H6 rejecting task: no slot_to_change")
            return False
            
        logger.info(f"H6 accepting task for slot: {slot_to_change}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Create specialized value."""
        logger.info("H6 then_compute starting")
        
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            logger.info("H6: Missing unit or task")
            return False
            
        # Get slot to specialize
        slot = task.supplemental.get('slot_to_change')
        if not slot or not unit.has_prop(slot):
            logger.info(f"H6: Invalid slot to change: {slot}")
            return False
            
        # Get and store old value
        old_value = unit.get_prop(slot)
        if old_value is None:
            logger.info("H6: No value to specialize")
            return False
            
        # Try specialization
        new_value = specialize_value(old_value)
        if new_value is None or new_value == old_value:
            logger.info("H6: Could not create specialized value")
            return False
            
        # Store results
        logger.info(f"H6: Specialized {slot} from {old_value} to {new_value}")
        context['old_value'] = old_value
        context['new_value'] = new_value
        context['slot_to_change'] = slot
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create new specialized unit."""
        logger.info("H6 then_define_new_concepts starting")
        
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        new_value = context.get('new_value')
        
        logger.info(f"H6: Checking requirements - unit: {unit}, slot: {slot}, new_value: {new_value}")
        if not all([unit, slot, new_value is not None]):
            logger.info("H6: Missing requirements for new unit")
            return False
        logger.info("H6: All requirements present")

        # Create specialized unit
        task_manager = context.get('task_manager')
        logger.info(f"H6: Got task manager: {task_manager}")
        if not task_manager:
            logger.info("H6: No task manager in context")
            return False
            
        unit_registry = task_manager.unit_registry
        logger.info(f"H6: Got unit registry: {unit_registry}")
        if not unit_registry:
            logger.info("H6: No unit registry from task manager")
            return False
            
        new_name = f"{unit.name}-{slot}-spec"
        logger.info(f"H6: Creating new unit {new_name}")
        
        new_unit = unit_registry.create_unit(new_name)
        if not new_unit:
            logger.info("H6: Failed to create new unit")
            return False
            
        # Copy properties
        logger.info(f"H6: Copying properties from {unit.name} to {new_name}")
        for key, value in unit.properties.items():
            if key != slot and key not in ['specializations', 'generalizations']:
                logger.info(f"H6: Copying property {key} = {value}")
                new_unit.set_prop(key, value)
                
        # Set specialized value
        logger.info(f"H6: Setting specialized value {slot} = {new_value}")
        new_unit.set_prop(slot, new_value)
        
        # Set worth
        worth = unit.worth_value()
        logger.info(f"H6: Original worth: {worth}")
        new_worth = int(worth * 0.9)
        logger.info(f"H6: Setting new worth: {new_worth}")
        new_unit.set_prop('worth', new_worth)
        
        # Update relationships
        logger.info(f"H6: Setting up specialization/generalization relationships")
        unit.add_to_prop('specializations', new_unit.name)
        new_unit.add_to_prop('generalizations', unit.name)
        
        # Register unit
        logger.info(f"H6: Registering new unit {new_name}")
        if not new_unit or not unit_registry.register(new_unit):
            logger.info("H6: Failed to register new unit")
            return False
            
        # Mark success
        logger.info(f"H6: Successfully created and registered unit {new_name}")
        
        # Get existing task results or create new ones
        task_results = context.get('task_results', {})
        if not task_results:
            task_results = {
                'status': 'in_progress',
                'new_tasks': [],
                'new_units': [],
                'success': True
            }
            context['task_results'] = task_results
        elif 'new_units' not in task_results:
            task_results['new_units'] = []
            
        # Add our new unit to task results
        # Log task results before adding new unit
        logger.info(f"H6: Task results before adding unit: {task_results}")
        
        task_results['new_units'].append(new_unit)
        task_results['status'] = 'completed'
        task_results['success'] = True
        
        # Log final results
        logger.info(f"H6: Final task results: {task_results}")
        
        logger.info(f"H6: Final task results with new unit: {task_results}")
        return True

    # Set the functions as properties on the heuristic
    heuristic.set_prop('if_potentially_relevant', if_potentially_relevant)
    heuristic.set_prop('then_compute', then_compute)
    heuristic.set_prop('then_define_new_concepts', then_define_new_concepts)
