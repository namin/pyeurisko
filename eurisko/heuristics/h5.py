"""H5 heuristic implementation."""
import random
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def write_debug(msg):
    with open('/tmp/h5_debug.log', 'a') as f:
        f.write(msg + '\n')
        f.flush()

def setup_h5(heuristic):
    """Configure H5 to select slots for specialization."""
    write_debug("[H5] Setting up")
    heuristic.set_prop('worth', 151)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN randomly select which slots to specialize")
    heuristic.set_prop('arity', 1)

    @rule_factory 
    def if_working_on_task(rule, context):
        write_debug("\n[H5] CHECKING TASK")
        unit = context.get('unit')
        task = context.get('task')
        
        if not all([unit, task]):
            write_debug("[H5] Missing unit or task")
            return False
            
        write_debug(f"[H5] Unit: {unit.name}")
        write_debug(f"[H5] Task type: {task.task_type}")
        write_debug(f"[H5] Supplemental: {task.supplemental}")
        
        # Find slots we could specialize
        specializable_slots = []
        for slot in ['domain', 'range', 'isa', 'applics']:
            if unit.has_prop(slot) and unit.get_prop(slot):
                value = unit.get_prop(slot)
                specializable_slots.append(slot)
                write_debug(f"[H5] Found slot {slot} = {value}")
        
        if not specializable_slots:
            write_debug("[H5] No specializable slots")
            return False
            
        context['specializable_slots'] = specializable_slots
        write_debug(f"[H5] Will try to specialize: {specializable_slots}")
        return True

    @rule_factory 
    def then_compute(rule, context):
        write_debug("\n[H5] COMPUTING")
        slots = context.get('specializable_slots', [])
        if not slots:
            write_debug("[H5] No slots to pick from")
            return False

        # Select one slot randomly
        slot = random.choice(slots)
        write_debug(f"[H5] Selected {slot} to specialize")
            
        # Store results
        context['slot_to_change'] = slot
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        slot = context.get('slot_to_change')
        if not slot:
            return False
            
        unit = context.get('unit')
        write_debug(f"[H5] Will specialize {unit.name}.{slot}")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        write_debug("\n[H5] ADDING TO AGENDA")
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        task_manager = rule.task_manager
        
        if not all([unit, slot, task_manager]):
            missing = []
            if not unit: missing.append('unit')
            if not slot: missing.append('slot')
            if not task_manager: missing.append('task_manager')
            write_debug(f"[H5] Missing required values: {missing}")
            return False

        # Create specialization task
        new_task = {
            'priority': 600,  # Higher than current task
            'unit': unit.name,
            'slot': slot,
            'task_type': 'specialization',
            'reasons': [f"Specializing {slot} of {unit.name}"],
            'supplemental': {
                'slot_to_change': slot,
                'credit_to': ['h5']
            }
        }
        
        write_debug("[H5] Creating new task:")
        for k, v in new_task.items():
            write_debug(f"  {k}: {v}")
            
        task_manager.add_task(new_task)

        # Mark success
        context['task_results'] = {
            'status': 'completed',
            'success': True,
            'new_tasks': [f"Added specialization task for {slot}"]
        }
        write_debug("[H5] Added task and marked success")
        return True