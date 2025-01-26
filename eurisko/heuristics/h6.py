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
    
    # Initialize record properties as functions (not tuples)
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_compute_record', record_func)
    heuristic.set_prop('then_define_new_concepts_record', record_func)
    heuristic.set_prop('then_print_to_user_record', record_func)
    heuristic.set_prop('overall_record', record_func)
    heuristic.set_prop('then_compute_failed_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we have a slot selected for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        return (task.get('task_type') == 'specialization' and
                'slot_to_change' in task)

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
            
        # Get data type and specialize
        data_type = unit.get_prop('data_type')
        
        # Specialize based on data type
        new_value = old_value
        if data_type == 'list' and isinstance(old_value, list):
            if len(old_value) > 1:
                new_value = random.sample(old_value, random.randint(1, len(old_value)))
        
        if new_value == old_value:
            logger.info(f"\nCouldn't find meaningful specialization of the {slot} "
                       f"slot of {unit.name}")
            return False
            
        context['old_value'] = old_value
        context['new_value'] = new_value
        context['slot'] = slot
        
        # Create new specialized unit with unit registry from rule
        new_unit = rule.unit_registry.create_unit(f"{unit.name}-spec")
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
        rule.unit_registry.register(new_unit)
        
        # Add to results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        context['task_results'] = task_results
        
        return True