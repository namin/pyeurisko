"""H6 heuristic implementation: Specialize a chosen slot."""
from typing import Any, Dict
from ..units import Unit
import logging
from ..heuristics import rule_factory
import random

logger = logging.getLogger(__name__)

def specialize_list(value):
    """Specializes a list value through various strategies."""
    if not value:
        return None
        
    strategies = [
        lambda x: random.sample(x, random.randint(1, len(x))),
        lambda x: x[:random.randint(1, len(x))],
        lambda x: x[-random.randint(1, len(x)):],
        lambda x: [i for i in x if isinstance(i, (str, int, float))][:random.randint(1, len(x))]
    ]
    
    for strategy in strategies:
        try:
            result = strategy(value)
            if result and result != value and len(result) < len(value):
                return result
        except Exception as e:
            logger.debug(f"H6 specialize_list strategy failed: {e}")
            continue
    return None

def specialize_str(value):
    """Specializes a string value."""
    if not value:
        return None
        
    strategies = [
        lambda x: f"{x}_specialized",
        lambda x: f"specific_{x}",
        lambda x: f"{x}_{random.randint(1,100)}"
    ]
    
    for strategy in strategies:
        try:
            result = strategy(value)
            if result and result != value:
                return result
        except Exception as e:
            logger.debug(f"H6 specialize_str strategy failed: {e}")
            continue
    return None

def specialize_number(value):
    """Specializes a numeric value."""
    if not isinstance(value, (int, float)):
        return None
        
    strategies = [
        lambda x: x * random.uniform(0.5, 0.9),
        lambda x: x + random.uniform(-x*0.1, x*0.1),
        lambda x: round(x / 5) * 5
    ]
    
    for strategy in strategies:
        try:
            result = strategy(value)
            if result and result != value:
                return result 
        except Exception as e:
            logger.debug(f"H6 specialize_number strategy failed: {e}")
            continue
    return None

def specialize_dict(value):
    """Specializes a dictionary value."""
    if not value:
        return None
        
    try:
        num_entries = random.randint(1, len(value))
        keys = random.sample(list(value.keys()), num_entries)
        result = {k: value[k] for k in keys}
        if result and result != value and len(result) < len(value):
            return result
    except Exception as e:
        logger.debug(f"H6 specialize_dict failed: {e}")
    return None

def specialize_value(value):
    """Specializes a value based on its type."""
    logger.debug(f"H6 specializing value of type {type(value)}: {value}")
    
    if isinstance(value, list):
        return specialize_list(value)
    elif isinstance(value, str):
        return specialize_str(value)
    elif isinstance(value, (int, float)):
        return specialize_number(value)
    elif isinstance(value, dict):
        return specialize_dict(value)
    return None

def setup_h6(heuristic) -> None:
    """Configure H6: Specialize a chosen slot."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to specialize a unit, and a slot has been chosen "
        "to be the one changed, THEN randomly select a part of it and specialize that part")
    heuristic.set_prop('abbrev', "Specialize a given slot of a given unit")
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Initial relevance check."""
        task = context.get('task')
        if not task:
            return False
            
        task_type = task.get('task_type')
        if task_type != 'specialization':
            return False
            
        supplemental = task.get('supplemental', {})
        if 'slot_to_change' not in supplemental:
            return False
            
        return True

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we have a slot selected for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            logger.debug("H6: Missing unit or task")
            return False
            
        if task.get('task_type') != 'specialization':
            logger.debug("H6: Not a specialization task") 
            return False
            
        supplemental = task.get('supplemental', {})
        if 'slot_to_change' not in supplemental:
            logger.debug("H6: No slot_to_change in supplemental")
            return False
            
        slot_to_change = supplemental.get('slot_to_change')
        if not slot_to_change or not unit.has_prop(slot_to_change):
            logger.debug(f"H6: Invalid slot {slot_to_change}")
            return False
            
        logger.debug(f"H6: Valid specialization task for slot {slot_to_change}")
        context['slot_to_change'] = slot_to_change
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print the specialization results."""
        unit = context.get('unit')
        old_value = context.get('old_value')
        new_value = context.get('new_value')
        slot = context.get('slot_to_change')
        
        if not all([unit, slot, old_value is not None, new_value is not None]):
            logger.debug("H6 then_print_to_user: Missing required values")
            return False
            
        if old_value == new_value:
            logger.debug("H6 then_print_to_user: No change in value")
            return False
            
        logger.info(f"\nSpecialized the {slot} slot of {unit.name}, replacing its old value "
                   f"({old_value}) by {new_value}.\n")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Perform the slot specialization."""
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        if not unit or not slot:
            logger.debug("H6 then_compute: Missing unit or slot")
            return False
            
        # Get current value
        old_value = unit.get_prop(slot)
        if old_value is None:
            logger.debug(f"H6 then_compute: No value found for slot {slot}")
            return False
            
        # Try specialization
        new_value = specialize_value(old_value)
        logger.debug(f"H6 new specialized value: {new_value}")
        
        if new_value is None or new_value == old_value:
            logger.debug(f"H6 then_compute: Failed to specialize {slot}")
            return False
            
        logger.debug(f"H6 then_compute: Successfully specialized {slot}")
        context['old_value'] = old_value
        context['new_value'] = new_value
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create the new specialized unit."""
        unit = context.get('unit')
        new_value = context.get('new_value')
        slot = context.get('slot_to_change')
        task = context.get('task')
        
        if not all([unit, new_value is not None, slot, task]):
            logger.debug("H6 then_define_new_concepts: Missing required values")
            return False
        
        # Create new specialized unit
        new_name = f"{unit.name}-{slot}-spec"
        logger.debug(f"H6 creating new unit: {new_name}")
        
        unit_registry = rule.unit_registry
        new_unit = unit_registry.create_unit(new_name)
        if not new_unit:
            logger.debug("H6 failed to create new unit")
            return False
            
        # Copy properties from original unit
        new_unit.set_prop('worth', unit.worth_value())
        for key, value in unit.properties.items():
            if key != slot and key not in ['specializations', 'generalizations', 'creditors']:
                new_unit.set_prop(key, value)
            
        # Set specialized value
        new_unit.set_prop(slot, new_value)
        
        # Update relationships
        unit.add_to_prop('specializations', new_unit.name)
        new_unit.add_to_prop('generalizations', unit.name)
        
        # Add credits
        creditors = task.get('supplemental', {}).get('credit_to', [])
        new_unit.add_to_prop('creditors', ['h6'] + list(creditors))
        
        # Add to unit registry
        if not unit_registry.register(new_unit):
            logger.debug("H6 failed to register new unit")
            return False
        
        # Ensure task_results exists and is a dict
        if 'task_results' not in context:
            context['task_results'] = {}
        task_results = context['task_results']
        
        # Initialize new_units list if needed
        if 'new_units' not in task_results:
            task_results['new_units'] = []
            
        # Add the new unit and update status
        task_results['new_units'].append(new_unit)
        task_results['status'] = 'completed'
        task_results['success'] = True
        
        logger.debug(f"H6 successfully created specialized unit {new_name}")
        return True