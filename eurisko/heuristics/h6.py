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
        if not task:
            return False
            
        if task.task_type != 'specialization':
            return False
            
        slot_to_change = task.supplemental.get('slot_to_change')
        logger.debug(f"H6 checking task with supplemental: {task.supplemental}")
        if not slot_to_change:
            logger.debug("H6 rejecting task: no slot_to_change")
            return False
            
        return True

    @rule_factory
    def then_compute(rule, context):
        """Create specialized value."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            return False
            
        # Get slot to specialize
        slot = task.supplemental.get('slot_to_change')
        if not slot or not unit.has_prop(slot):
            return False
            
        # Get and store old value
        old_value = unit.get_prop(slot)
        if old_value is None:
            return False
            
        # Try specialization
        new_value = specialize_value(old_value)
        if new_value is None or new_value == old_value:
            return False
            
        # Store results
        context['old_value'] = old_value
        context['new_value'] = new_value
        context['slot_to_change'] = slot
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create new specialized unit."""
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        new_value = context.get('new_value')
        
        if not all([unit, slot, new_value is not None]):
            return False

        # Create specialized unit
        unit_registry = rule.unit_registry
        new_name = f"{unit.name}-{slot}-spec"
        new_unit = unit_registry.create_unit(new_name)
        if not new_unit:
            return False
            
        # Copy properties
        for key, value in unit.properties.items():
            if key != slot and key not in ['specializations', 'generalizations']:
                new_unit.set_prop(key, value)
                
        # Set specialized value
        new_unit.set_prop(slot, new_value)
        new_unit.set_prop('worth', int(unit.worth_value() * 0.9))
        
        # Update relationships
        unit.add_to_prop('specializations', new_unit.name)
        new_unit.add_to_prop('generalizations', unit.name)
        
        # Register unit
        if not unit_registry.register(new_unit):
            return False
            
        # Mark success
        context['task_results'] = {
            'status': 'completed',
            'success': True,
            'new_units': [new_unit]
        }
        return True