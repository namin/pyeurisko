"""H5 heuristic implementation."""
import random
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h5(heuristic):
    """Configure H5 to select slots for specialization."""
    heuristic.set_prop('worth', 151)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN randomly select which slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular slots of u to specialize")
    heuristic.set_prop('arity', 1)

    # Add record functions that return True to indicate success
    def then_compute_record(rule, context):
        return True
        
    def then_add_to_agenda_record(rule, context):
        return True
        
    def overall_record(rule, context):
        return True
        
    heuristic.set_prop('then_compute_record', then_compute_record)
    heuristic.set_prop('then_add_to_agenda_record', then_add_to_agenda_record)
    heuristic.set_prop('overall_record', overall_record)

    @rule_factory 
    def if_potentially_relevant(rule, context):
        """Check if we're working on specialization."""
        task = context.get('task')
        if not task:
            return False
            
        if task.task_type != 'specialization':
            return False
            
        if 'slot_to_change' in task.supplemental:
            return False
            
        return True

    @rule_factory 
    def then_compute(rule, context):
        """Pick a slot to specialize."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Find important slots that have values
        slots = []
        for slot in ['domain', 'range', 'isa', 'applics']:
            if unit.has_prop(slot) and unit.get_prop(slot):
                slots.append(slot)
                
        if not slots:
            return False
            
        # Pick one randomly
        slot = random.choice(slots)
        context['slot_to_change'] = slot
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Create task to specialize chosen slot."""
        unit = context.get('unit')
        slot = context.get('slot_to_change') 
        task_manager = rule.task_manager
        
        if not all([unit, slot, task_manager]):
            return False

        # Create task with chosen slot
        new_task = {
            'priority': 600,
            'unit': unit.name,
            'slot': slot,
            'task_type': 'specialization',
            'reasons': [f"Specializing {slot} of {unit.name}"],
            'supplemental': {
                'slot_to_change': slot,
                'credit_to': ['h5']
            }
        }
        
        task_manager.add_task(new_task)

        # Mark success
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [f"Added specialization task for {slot}"]
        task_results['status'] = 'completed'
        task_results['success'] = True
        context['task_results'] = task_results
        return True