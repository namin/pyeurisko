"""H6 heuristic implementation: Specialize a chosen slot."""
from typing import Any, Dict
from ..units import Unit
import logging

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
    
    # Set record counts from original
    heuristic.set_prop('then_compute_record', (58183, 73))
    heuristic.set_prop('then_define_new_concepts_record', (74674, 73))
    heuristic.set_prop('then_print_to_user_record', (31470, 73))
    heuristic.set_prop('overall_record', (188387, 73))
    heuristic.set_prop('then_compute_failed_record', (24908, 56))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we have a slot selected for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        return (task.get('task_type') == 'specialization' and
                'slot_to_change' in task)

    def print_results(context: Dict[str, Any]) -> bool:
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

    def compute_action(context: Dict[str, Any]) -> bool:
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
        new_value = specialize_value(old_value, data_type)
        
        if new_value == old_value:
            logger.info(f"\nCouldn't find meaningful specialization of the {slot} "
                       f"slot of {unit.name}")
            return False
            
        context['old_value'] = old_value
        context['new_value'] = new_value
        context['slot'] = slot
        
        # Create new specialized unit
        new_unit = Unit(f"{unit.name}-spec", unit.worth_value())
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
        
        # Add to results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        context['task_results'] = task_results
        
        return True

    def specialize_value(value: Any, data_type: str) -> Any:
        """Specialize a value based on its data type."""
        if data_type == 'list' and isinstance(value, list):
            import random
            if len(value) <= 1:
                return value
            return random.sample(value, random.randint(1, len(value)))
            
        # For now, other types return unchanged
        # TODO: Implement other specialization types
        return value

    # Configure the heuristic
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)
