"""H6 heuristic implementation: Specialize a chosen slot."""
from typing import Any, Dict
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h6(heuristic) -> None:
    """Configure H6: Specialize a chosen slot of a unit."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we have a slot to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        return (task.get('task_type') == 'specialization' and
                task.get('slot_to_change'))

    def compute_action(context: Dict[str, Any]) -> bool:
        """Specialize the chosen slot."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        slot_to_change = task.get('slot_to_change')
        if not slot_to_change:
            return False
            
        # Get current value
        old_value = unit.get_prop(slot_to_change)
        if old_value is None:
            logger.warning(f"No value found for slot {slot_to_change} in unit {unit.name}")
            return False
            
        # Create specialized value based on data type
        new_value = None
        data_type = unit.get_prop('data_type')
        
        if data_type == 'list':
            new_value = specialize_list(old_value)
        elif data_type == 'function':
            new_value = specialize_function(old_value)
        elif data_type == 'predicate':
            new_value = specialize_predicate(old_value)
        else:
            logger.warning(f"Unsupported data type {data_type} for specialization")
            return False
            
        if new_value == old_value:
            logger.debug("Specialization produced no change")
            return False
            
        # Create new unit as specialization
        new_unit = Unit(f"{unit.name}-specialized", unit.worth_value())
        new_unit.copy_slots_from(unit)
        new_unit.set_prop(slot_to_change, new_value)
        
        # Register the new unit
        heuristic.unit_registry.register(new_unit)
        
        # Update relationships
        unit.add_to_prop('specializations', new_unit.name)
        new_unit.add_to_prop('generalizations', unit.name)
        
        # Add to task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        
        return True

    def specialize_list(value: list) -> list:
        """Create a more specific version of a list."""
        if not value:
            return value
        # Here we could implement various specialization strategies:
        # - Take subset
        # - Add constraints
        # - Make elements more specific
        # For now we'll just return a subset
        import random
        if len(value) <= 1:
            return value
        return random.sample(value, random.randint(1, len(value)))

    def specialize_function(value: Any) -> Any:
        """Create a more specific version of a function."""
        # This would involve analyzing the function and creating a more
        # specialized version, e.g., by adding preconditions or constraints
        # For now we just return the original
        return value

    def specialize_predicate(value: Any) -> Any:
        """Create a more specific version of a predicate."""
        # This would involve creating a more restrictive predicate 
        # For now we just return the original
        return value

    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)