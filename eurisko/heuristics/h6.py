"""H6 heuristic implementation: Specialize a chosen slot."""
from typing import Any, Dict
from ..units import Unit
import logging
from ..heuristics import rule_factory
import random

logger = logging.getLogger(__name__)

def setup_h6(heuristic) -> None:
    """Configure H6: Specialize a chosen slot of a unit."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to specialize a unit, and a slot has been chosen "
        "to be the one changed, THEN randomly select a part of it and specialize that part")
    heuristic.set_prop('abbrev', "Specialize a given slot of a given unit")
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we have a slot selected for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if not task.get('task_type') == 'specialization':
            return False
            
        if 'slot_to_change' not in task:
            return False
            
        slot_to_change = task.get('slot_to_change')
        if not slot_to_change or not unit.has_prop(slot_to_change):
            return False
            
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print the specialization results."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        slot = task.get('slot_to_change')
        old_value = context.get('old_value')
        new_value = context.get('new_value')
        
        if not all([slot, old_value is not None, new_value is not None]):
            return False
            
        if old_value == new_value:
            return False
            
        logger.info(f"\nSpecialized the {slot} slot of {unit.name}, replacing its old value "
                   f"({old_value}) by {new_value}.\n")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Perform the slot specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        slot = task.get('slot_to_change')
        if not slot:
            return False
            
        # Get current value
        old_value = unit.get_prop(slot)
        if old_value is None:
            logger.warning(f"No value found for slot {slot} in unit {unit.name}")
            return False
            
        # Specialize based on data type and value
        new_value = None
        if isinstance(old_value, list) and old_value:
            # Take a subset for lists
            new_size = random.randint(1, len(old_value))
            new_value = random.sample(old_value, new_size)
        elif isinstance(old_value, str):
            # For strings, we could specialize by making more specific
            new_value = old_value + "_specialized"
        elif isinstance(old_value, (int, float)):
            # For numbers, we could restrict the range
            new_value = old_value * random.uniform(0.5, 0.9) 
        
        if new_value is None or new_value == old_value:
            logger.info(f"\nCouldn't find meaningful specialization of the {slot} "
                       f"slot of {unit.name}")
            return False
            
        context['old_value'] = old_value
        context['new_value'] = new_value
        context['slot'] = slot
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create the new specialized unit."""
        unit = context.get('unit')
        task = context.get('task')
        new_value = context.get('new_value')
        slot = context.get('slot')
        
        if not all([unit, task, new_value is not None, slot]):
            return False
        
        # Create new specialized unit 
        new_unit = rule.unit_registry.create_unit(f"{unit.name}-spec")
        if not new_unit:
            return False
            
        new_unit.set_prop('worth', unit.worth_value())
        new_unit.copy_slots_from(unit)
            
        # Set specialized value
        new_unit.set_prop(slot, new_value)
        
        # Update relationships
        unit.add_to_prop('specializations', new_unit.name)
        new_unit.add_to_prop('generalizations', unit.name)
        
        # Add credits
        creditors = task.get('credit_to', [])
        if creditors:
            new_unit.add_to_prop('creditors', ['h6'] + list(creditors))
        
        # Add to unit registry
        if not rule.unit_registry.register(new_unit):
            return False
        
        # Add to results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        context['task_results'] = task_results
        
        return True