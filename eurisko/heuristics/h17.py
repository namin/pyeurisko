"""H17 heuristic implementation: Select slots for generalization."""
from typing import Any, Dict, List, Optional
from ..units import Unit
import logging
import random
from ..heuristics import rule_factory

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

    def assess_slot_worth(slot: str, unit: Unit) -> float:
        """Calculate relative worth of generalizing a slot."""
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

    @rule_factory
    def if_working_on_task(rule, context):
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

    @rule_factory
    def then_compute(rule, context):
        """Select slots and update task context."""
        unit = context.get('unit')
        task = context.get('task')
        
        if not unit or not task:
            return False
            
        # Get available slots and calculate their worths
        available_slots = unit.get_prop('slots', [])
        if not available_slots:
            return False
            
        slot_worths = {
            slot: assess_slot_worth(slot, unit)
            for slot in available_slots
        }
        
        # Weighted random selection
        max_slots = 3
        total_worth = sum(slot_worths.values())
        selected = []
        
        if total_worth == 0:
            selected = random.sample(
                available_slots,
                min(max_slots, len(available_slots))
            )
        else:
            remaining_slots = list(available_slots)
            while len(selected) < max_slots and remaining_slots:
                weights = [slot_worths[s]/total_worth for s in remaining_slots]
                chosen = random.choices(remaining_slots, weights=weights)[0]
                selected.append(chosen)
                remaining_slots.remove(chosen)
        
        if not selected:
            return False
            
        # Store selection results with worth assessments
        context['selected_slots'] = selected
        context['slot_worths'] = {
            slot: slot_worths[slot]
            for slot in selected
        }
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Explain slot selection rationale."""
        unit = context.get('unit')
        slots = context.get('selected_slots', [])
        slot_worths = context.get('slot_worths', {})
        
        if not unit or not slots:
            return False
            
        slot_details = []
        for slot in slots:
            worth = slot_worths.get(slot, 0)
            is_criterial = slot in (unit.get_prop('criterial_slots') or [])
            detail = f"{slot} (worth: {worth:.0f}{', criterial' if is_criterial else ''})"
            slot_details.append(detail)
            
        logger.info(
            f"\n{unit.name} will be generalized by considering the following slots:\n"
            f"{', '.join(slot_details)}\n"
        )
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks for each selected slot."""
        unit = context.get('unit')
        task = context.get('task')
        selected_slots = context.get('selected_slots', [])
        slot_worths = context.get('slot_worths', {})
        
        if not all([unit, task, selected_slots]):
            return False
            
        base_priority = task.get('priority', 500)
        worth_stats = task.get('supplemental', {}).get('worth_stats', {})
        success_ratio = worth_stats.get('success_ratio', 0.5)
        
        for slot in selected_slots:
            slot_worth = slot_worths.get(slot, 100)
            
            # Calculate priority based on slot assessment and unit performance
            priority = int(
                base_priority * 
                (slot_worth / 100) * 
                (0.5 + success_ratio)
            )
            
            new_task = {
                'priority': priority,
                'unit': unit.name,
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
            
            if not rule.task_manager.add_task(new_task):
                continue
        
        context['task_results'] = {
            'new_tasks': f"{len(selected_slots)} slots selected for generalization"
        }
        return True