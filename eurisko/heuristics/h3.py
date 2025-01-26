"""H3 heuristic implementation: Choose slot to specialize."""
from typing import Any, Dict, Callable
import random
import logging

logger = logging.getLogger(__name__)

def setup_h3(heuristic) -> None:
    """Configure H3: Choose slot to specialize."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 101)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, but no specific slot to "
        "specialize is yet known, THEN choose one")
    heuristic.set_prop('abbrev', "Randomly choose a slot to specialize")
    heuristic.set_prop('arity', 1)

    def if_working_on_task_factory(rule) -> Callable:
        """Factory function that returns the test function."""
        def check_task(context: Dict[str, Any]) -> bool:
            """Check if we need to choose a slot to specialize."""
            unit = context.get('unit')
            task = context.get('current_task')  # Changed from task to current_task
            if not unit or not task:
                return False
                
            # Check if this is a specialization task without a chosen slot
            is_specialization = task.task_type == 'specialization'  # Changed to use Task attribute
            no_slot_chosen = 'slot_to_change' not in task.supplemental  # Check supplemental dict
            
            # Get task manager from rule since it's closed over
            task_manager = rule.task_manager
            if task_manager:
                similar_tasks = sum(1 for t in task_manager.agenda
                                  if (t.unit_name == unit.name and 
                                      t.task_type == 'specialization'))
                too_many_tasks = similar_tasks >= 11
                if too_many_tasks:
                    return False
                    
            return is_specialization and no_slot_chosen
        return check_task

    def then_print_to_user_factory(rule) -> Callable:
        """Factory function that returns the print action."""
        def print_action(context: Dict[str, Any]) -> bool:
            """Print explanation of slot choice."""
            unit = context.get('unit')
            slot = context.get('chosen_slot')
            reason = context.get('reason')
            
            if not all([unit, slot, reason]):
                return False
                
            logger.info(f"\n{reason}")
            return True
        return print_action

    def then_compute_factory(rule) -> Callable:
        """Factory function that returns compute action."""
        def compute_action(context: Dict[str, Any]) -> bool:
            """Randomly select a slot for specialization."""
            unit = context.get('unit')
            task = context.get('current_task')
            if not unit or not task:
                return False

            # Get slots from rule's registry
            unit_slots = unit.get_prop('slots') or []
            slot_types = rule.unit_registry.get_units_by_category('slot')
            valid_slots = set(unit_slots) & set(slot_types)
            slots = list(valid_slots) if valid_slots else unit_slots

            if not slots:
                return False

            # Choose slot and update context
            chosen_slot = random.choice(slots)
            task.supplemental['slot_to_change'] = chosen_slot  # Update in supplemental
            context['chosen_slot'] = chosen_slot
            
            # Store credit information
            task_creditors = task.supplemental.get('creditors', [])
            task.supplemental['creditors'] = task_creditors + ['h3']
            
            # Create reason text
            reason = (f"A new unit will be created by specializing the {chosen_slot} slot "
                     f"of {unit.name}; that slot was chosen randomly.")
            context['reason'] = reason
            
            return True
        return compute_action

    def then_add_to_agenda_factory(rule) -> Callable:
        """Factory function that returns agenda action."""
        def add_to_agenda(context: Dict[str, Any]) -> bool:
            """Add specialized task to agenda."""
            unit = context.get('unit')
            task = context.get('current_task')
            chosen_slot = context.get('chosen_slot')
            reason = context.get('reason')
            
            if not all([unit, task, chosen_slot, reason]):
                return False
                
            task_manager = rule.task_manager  # Get from rule
            if not task_manager:
                return False
                
            # Calculate priority based on worths
            base_priority = task.priority 
            h3_worth = rule.worth_value()  # Use rule not heuristic
            unit_worth = unit.worth_value()
            new_priority = (base_priority + h3_worth + unit_worth) // 3
            
            # Create new task using Task class
            from ..tasks import Task  # Import here to avoid circular
            new_task = Task(
                priority=new_priority,
                unit_name=unit.name,
                slot_name='specializations',
                reasons=[reason],
                task_type='specialization',
                supplemental={
                    'slot_to_change': chosen_slot,
                    'creditors': ['h3'] + task.supplemental.get('creditors', [])
                }
            )
            
            task_manager.add_task(new_task)
            
            # Record in task results
            task.results['new_tasks'] = [
                f"1 specific slot of {unit.name} to find specializations of"
            ]
            
            return True
        return add_to_agenda

    # Set up all the factory functions
    heuristic.set_prop('if_working_on_task', if_working_on_task_factory)
    heuristic.set_prop('then_print_to_user', then_print_to_user_factory)
    heuristic.set_prop('then_compute', then_compute_factory)
    heuristic.set_prop('then_add_to_agenda', then_add_to_agenda_factory)
    
    # Add subsumption information from LISP
    heuristic.set_prop('subsumed_by', ['h5', 'h5-criterial', 'h5-good'])
