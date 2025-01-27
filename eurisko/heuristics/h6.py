"""H6 heuristic implementation: Specialize a chosen slot."""
import logging
import random
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
        return int(value * 0.9)  # Reduce by 10%

    return None

def setup_h6(heuristic):
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to specialize a unit, and a slot has been chosen "
        "to be the one changed, THEN specialize that slot's value")
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_working_on_task(rule, context):
        logger.debug("\n---H6 WORKING ON TASK---")
        unit = context.get('unit')
        task = context.get('task')
        
        if not all([unit, task]):
            logger.debug("Missing unit or task")
            return False
            
        logger.debug(f"Unit: {unit.name}")
        logger.debug(f"Task type: {task.task_type}")
        logger.debug(f"Supplemental: {task.supplemental}")
            
        # Get slot to specialize
        slot = task.supplemental.get('slot_to_change')
        if not slot:
            logger.debug("No slot_to_change in supplemental")
            return False

        if not unit.has_prop(slot):
            logger.debug(f"Unit doesn't have slot {slot}")
            return False
        
        # Get current value
        value = unit.get_prop(slot)
        if value is None:
            logger.debug(f"Slot {slot} has no value")
            return False
            
        # Store for then_compute
        context['slot_to_change'] = slot
        context['old_value'] = value
        logger.debug(f"Will specialize {slot} = {value}")
        return True

    @rule_factory
    def then_compute(rule, context):
        logger.debug("\n---H6 COMPUTING---")
        old_value = context.get('old_value')
        if old_value is None:
            logger.debug("No old value")
            return False
            
        # Try specialization
        new_value = specialize_value(old_value)
        logger.debug(f"Trying to specialize {old_value}")
        
        if new_value is None or new_value == old_value:
            logger.debug("Specialization failed")
            return False
            
        logger.debug(f"Successfully specialized to {new_value}")
        context['new_value'] = new_value
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        old_value = context.get('old_value')
        new_value = context.get('new_value')
        
        if not all([unit, slot, old_value is not None, new_value is not None]):
            return False
            
        logger.info(f"\nH6: For {unit.name}.{slot}: {old_value} -> {new_value}")
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        logger.debug("\n---H6 CREATING NEW UNIT---")
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        new_value = context.get('new_value')
        
        if not all([unit, slot, new_value is not None]):
            missing = []
            if not unit: missing.append('unit')
            if not slot: missing.append('slot')
            if new_value is None: missing.append('new_value')
            logger.debug(f"Missing required values: {missing}")
            return False

        # Create new specialized unit
        unit_registry = rule.unit_registry
        new_name = f"{unit.name}-{slot}-spec"
        logger.debug(f"Creating unit {new_name}")
        
        new_unit = unit_registry.create_unit(new_name)
        if not new_unit:
            logger.debug("Failed to create unit")
            return False
            
        # Copy properties
        for key, value in unit.properties.items():
            if key != slot and key not in ['specializations', 'generalizations']:
                new_unit.set_prop(key, value)
                logger.debug(f"Copied {key} = {value}")
                
        # Set specialized value
        new_unit.set_prop(slot, new_value)
        new_unit.set_prop('worth', int(unit.worth_value() * 0.9))
        logger.debug(f"Set {slot} = {new_value}")
        
        # Update relationships
        unit.add_to_prop('specializations', new_unit.name)
        new_unit.add_to_prop('generalizations', unit.name)
        logger.debug("Updated relationships")
        
        # Register new unit
        if not unit_registry.register(new_unit):
            logger.debug("Failed to register unit")
            return False
            
        # Mark success
        context['task_results'] = {
            'status': 'completed',
            'success': True,
            'new_units': [new_unit]
        }
        logger.debug("Updated task results")
        return True