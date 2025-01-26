"""H17 heuristic implementation: Select slots for generalization."""
from typing import Any, Dict, List, Optional
from ..units import Unit
import logging
import random

logger = logging.getLogger(__name__)

def setup_h17(heuristic) -> None:
    """Configure H17: Choose slots for generalization.
    
    This heuristic handles the mechanics of selecting which slots to consider
    when attempting to generalize a concept. It uses both random selection and
    worth-based weighting to identify promising slots.
    """
    # Set properties from original Eurisko
    heuristic.set_prop('worth', 600)
    heuristic.set_prop('english',
        "IF the current task is to generalize a unit, and no slot has been chosen "
        "for modification, THEN intelligently select which slots to consider for "
        "generalization based on both random sampling and worth assessment.")
    heuristic.set_prop('abbrev', "Choose slots to generalize")
    
    # Initialize record keeping
    heuristic.set_prop('then_compute_record', (430, 4))
    heuristic.set_prop('then_add_to_agenda_record', (688, 4))
    heuristic.set_prop('then_print_to_user_record', (435, 4))
    heuristic.set_prop('overall_record', (1943, 4))
    heuristic.set_prop('arity', 1)

    def is_generalization_task(context: Dict[str, Any]) -> bool:
        """Check if current task is for generalization without selected slots."""
        task = context.get('task')
        if not task:
            return False
            
        task_type = task.get('task_type')
        supplemental = task.get('supplemental') or {}
        return (
            task_type == 'generalization' and
            'slot_to_change' not in supplemental
        )

    def assess_slot_worth(slot: str, unit: Unit) -> float:
        """Calculate relative worth of generalizing a slot.
        
        Considers:
        - Slot's current worth
        - Whether slot is marked as criterial
        - Historical success in generalizing this slot
        - Complexity of current slot value
        """
        base_worth = unit.get_prop(f'{slot}_worth', 100)
        
        # Bonus for criterial slots
        if slot in (unit.get_prop('criterial_slots') or []):
            base_worth *= 1.5
            
        # Penalty for very complex values to prefer simpler generalizations
        value = unit.get_prop(slot)
        if isinstance(value, (list, dict)):
            complexity_penalty = 0.8 ** len(str(value))
            base_worth *= complexity_penalty
            
        return base_worth

    def select_slots_to_generalize(unit: Unit, max_slots: int = 3) -> List[str]:
        """Choose slots for generalization using worth-weighted random selection."""
        available_slots = unit.get_prop('slots', [])
        if not available_slots:
            return []
            
        # Calculate worth for each slot
        slot_worths = {
            slot: assess_slot_worth(slot, unit)
            for slot in available_slots
        }
        
        # Weighted random selection
        total_worth = sum(slot_worths.values())
        if total_worth == 0:
            return random.sample(
                available_slots,
                min(max_slots, len(available_slots))
            )
            
        selected = []
        remaining_slots = list(available_slots)
        
        while len(selected) < max_slots and remaining_slots:
            weights = [slot_worths[s]/total_worth for s in remaining_slots]
            chosen = random.choices(remaining_slots, weights=weights)[0]
            selected.append(chosen)
            remaining_slots.remove(chosen)
            
        return selected

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Explain slot selection rationale."""
        unit = context.get('unit')
        slots = context.get('selected_slots', [])
        
        if not unit or not slots:
            return False
            
        slot_details = []
        for slot in slots:
            worth = assess_slot_worth(slot, unit)
            is_criterial = slot in (unit.get_prop('criterial_slots') or [])
            detail = f"{slot} (worth: {worth:.0f}{', criterial' if is_criterial else ''})"
            slot_details.append(detail)
            
        logger.info(
            f"\n{unit.name} will be generalized by considering the following slots:\n"
            f"{', '.join(slot_details)}\n"
        )
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Select slots and update task context."""
        unit = context.get('unit')
        task = context.get('task')
        
        if not unit or not task:
            return False
            
        # Just select slots and store in context for add_to_agenda to use
        selected_slots = select_slots_to_generalize(unit)
        if not selected_slots:
            return False
            
        # Store in context for add_to_agenda but don't modify task
        context['selected_slots'] = selected_slots
        return True

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add tasks for each selected slot."""
        unit = context.get('unit')
        system = context.get('system')
        task = context.get('task')
        selected_slots = context.get('selected_slots', [])
        
        if not all([unit, system, task, selected_slots]):
            return False
            
        base_priority = task.get('priority', 500)
        worth_stats = task.get('supplemental', {}).get('worth_stats', {})
        
        new_tasks = []
        for slot in selected_slots:
            slot_worth = assess_slot_worth(slot, unit)
            
            # Calculate priority based on slot assessment and unit performance
            success_ratio = worth_stats.get('success_ratio', 0.5)
            priority = int(
                base_priority * 
                (slot_worth / 100) * 
                (0.5 + success_ratio)
            )
            
            new_task = {
                'priority': priority,
                'unit': unit,
                'slot': 'generalizations',
                'reasons': [
                    f"Generalizing {slot} slot of {unit.name} "
                    f"(worth: {slot_worth:.0f})"
                ],
                'supplemental': {
                    'credit_to': ['h17'],
                    'slot_to_change': slot,
                    'task_type': 'generalization',
                    'worth_stats': worth_stats
                }
            }
            
            new_tasks.append(new_task)
            
        # Store results in context
        context['task_results'] = {
            'new_tasks': new_tasks
        }
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_working_on_task', is_generalization_task)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)
