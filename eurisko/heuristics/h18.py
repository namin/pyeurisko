"""H18 heuristic implementation: Execute slot generalization."""
from typing import Any, Dict, Optional, Tuple
from ..units import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h18(heuristic) -> None:
    """Configure H18: Execute generalization on selected slots.
    
    This heuristic performs the actual generalization of a unit's slot once h17
    has selected which slots to generalize. It includes sophisticated mechanisms
    for tracking changes, rewarding successful generalizations, and maintaining
    a record of the generalization process.
    """
    # Set properties from original Eurisko
    heuristic.set_prop('worth', 704)
    heuristic.set_prop('english',
        "IF the current task is to generalize a unit, and a slot has been chosen "
        "for modification, THEN systematically generalize that slot while tracking "
        "the changes and their impact.")
    heuristic.set_prop('abbrev', "Generalize a given slot of a given unit")
    
    # Initialize record keeping from original
    heuristic.set_prop('then_compute_failed_record', (5658, 17))
    heuristic.set_prop('then_compute_record', (3974, 13))
    heuristic.set_prop('then_define_new_concepts_record', (5740, 13))
    heuristic.set_prop('then_print_to_user_record', (2147, 13))
    heuristic.set_prop('overall_record', (13078, 13))
    heuristic.set_prop('arity', 1)

    def check_task_relevance(context: Dict[str, Any]) -> bool:
        """Verify task is for generalization with a selected slot."""
        task = context.get('task')
        if not task:
            return False
            
        # Check both supplemental and direct task slots for flexibility
        supplemental = task.get('supplemental') or {}
        slot_to_change = (
            'slot_to_change' in supplemental or
            'slot_to_change' in task or
            bool(task.get('slots_to_change'))
        )
        return task.get('task_type') == 'generalization' and slot_to_change

    def get_slot_generalizer(slot_type: str) -> Optional[str]:
        """Determine appropriate generalization function for slot type."""
        generalization_map = {
            'lisp_pred': 'generalize_lisp_pred',
            'lisp_fn': 'generalize_lisp_fn',
            'list': 'generalize_list',
            None: 'generalize_nil'  # Fallback for unknown types
        }
        return generalization_map.get(slot_type)

    def generalize_slot_value(old_value: Any, slot_type: str) -> Tuple[Any, Dict[str, Any]]:
        """Generalize a slot value based on its type.
        
        Returns:
            Tuple of (new_value, metadata) where metadata includes:
            - changes: List of specific changes made
            - units_involved: List of units referenced in generalization
            - generalization_method: Method used for generalization
        """
        metadata = {
            'changes': [],
            'units_involved': [],
            'generalization_method': None
        }
        
        if slot_type == 'lisp_pred':
            # Handle predicate generalization
            new_value, pred_changes = generalize_predicate(old_value)
            metadata['changes'].extend(pred_changes)
            metadata['generalization_method'] = 'predicate'
            
        elif slot_type == 'list':
            # Handle list generalization
            new_value, list_changes = generalize_list_value(old_value)
            metadata['changes'].extend(list_changes)
            metadata['generalization_method'] = 'list'
            
        else:
            # Default generalization
            new_value = old_value
            metadata['generalization_method'] = 'identity'
            
        return new_value, metadata

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Explain generalization process and results."""
        unit = context.get('unit')
        slot = context.get('task', {}).get('supplemental', {}).get('slot_to_change')
        old_value = context.get('old_value')
        new_value = context.get('new_value')
        
        if not all([unit, slot, old_value is not None, new_value is not None]):
            return False
            
        changes = context.get('generalization_metadata', {}).get('changes', [])
        
        logger.info(
            f"\nGeneralized the {slot} slot of {unit.name}:\n"
            f"Old value: {old_value}\n"
            f"New value: {new_value}\n"
            f"Changes made: {', '.join(changes) if changes else 'No changes required'}\n"
        )
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Execute the generalization process."""
        unit = context.get('unit')
        task = context.get('task')
        
        if not unit or not task:
            return False
            # Try to get slot_to_change from various places
        supplemental = task.get('supplemental') or {}
        slot = (
            supplemental.get('slot_to_change') or
            task.get('slot_to_change') or
            (task.get('slots_to_change') or [None])[0]
        )
        if not slot:
            return False
            
        old_value = unit.get_prop(slot)
        
        # Store old value in context
        context['old_value'] = old_value
        
        # Determine slot type and get appropriate generalizer
        slot_type = unit.get_prop(f'{slot}_type')
        
        # Perform generalization
        new_value, metadata = generalize_slot_value(old_value, slot_type)
        
        # Store results in context
        context['new_value'] = new_value
        context['generalization_metadata'] = metadata
        
        # Check if we actually generalized anything
        if new_value == old_value:
            logger.info(f"No meaningful generalization found for {slot} slot of {unit.name}")
            return False
            
        return True

    def define_new_concepts(context: Dict[str, Any]) -> bool:
        """Create new unit with generalized slot value."""
        unit = context.get('unit')
        system = context.get('system')
        new_value = context.get('new_value')
        task = context.get('task')
        
        if not all([unit, system, new_value is not None, task]):
            return False
            
        # Create new generalized unit
        new_unit = system.create_unit(f"{unit.name}_gen", unit.name)
        
        # Get slot same way as compute_action
        supplemental = task.get('supplemental') or {}
        slot = (
            supplemental.get('slot_to_change') or
            task.get('slot_to_change') or
            (task.get('slots_to_change') or [None])[0]
        )
        if not slot:
            return False
        for old_slot in unit.get_prop('slots', []):
            if old_slot != slot:
                new_unit.set_prop(old_slot, unit.get_prop(old_slot))
                
        # Set the generalized slot
        new_unit.set_prop(slot, new_value)
        
        # Update relationships
        new_unit.add_to_prop('generalizations', unit.name)
        unit.add_to_prop('specializations', new_unit.name)
        
        # Add creation record
        creation_record = {
            'task_num': task.get('task_num'),
            'by': 'h18',
            'slot_changed': slot,
            'from_unit': unit.name,
            'changes': context.get('generalization_metadata', {}).get('changes', [])
        }
        new_unit.set_prop('creation_record', creation_record)
        
        # Update task results
        system.add_task_result('new_units', [new_unit.name])
        
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_working_on_task', check_task_relevance)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_define_new_concepts', define_new_concepts)
