"""H12 heuristic implementation: Create rules to prevent mistakes."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h12(heuristic) -> None:
    """Configure H12: Form rules that would have prevented mistakes."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF C is about to die, then try to form a new heuristic, one which -- had "
        "it existed earlier -- would have prevented C from ever being defined in "
        "the first place")
    heuristic.set_prop('abbrev', "Form a rule that would have prevented this mistake")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_define_new_concepts', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check if unit is about to be deleted."""
        unit = context.get('unit')
        if not unit:
            return False
            
        deleted_units = context.get('task_results', {}).get('deleted_units', {}).get('units', [])
        return unit in deleted_units

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of preventative rule."""
        unit = context.get('unit')
        c_slot = context.get('c_slot')
        g_slot = context.get('g_slot')
        if not all([unit, c_slot, g_slot]):
            return False
            
        logger.info(f"\n\nJust before destroying a losing concept, Eurisko generalized "
                   f"from that bad experience, in the following way: Eurisko will no "
                   f"longer alter the {c_slot} slot of a unit when trying to find "
                   f"{g_slot} of that unit. We learned our lesson from {unit.name}\n")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Extract task and slot information."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Get creating task info
        creditors = unit.get_prop('creditors', [])
        if not creditors:
            return False
            
        creator = rule.unit_registry.get_unit(creditors[0])
        if not creator:
            return False
            
        # Find the task that created this unit
        creator_apps = creator.get_prop('applications', [])
        creation_task = None
        for app in creator_apps:
            if app.get('results') and unit in app['results']:
                creation_task = app.get('task')
                break
                
        if not creation_task:
            return False
            
        # Extract slot information
        c_slot = creation_task.get('supplemental', {}).get('slot_to_change')
        g_slot = creation_task.get('slot')
        if not c_slot or not g_slot:
            return False
            
        context['c_slot'] = c_slot
        context['g_slot'] = g_slot
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create preventative rule unit."""
        unit = context.get('unit')
        c_slot = context.get('c_slot')
        g_slot = context.get('g_slot')
        if not all([unit, c_slot, g_slot]):
            return False
            
        # Create new avoid rule
        new_unit = rule.unit_registry.create_unit('h-avoid')
        if not new_unit:
            return False
            
        # Set properties from context
        new_unit.set_prop('g_slot', g_slot)
        new_unit.set_prop('c_slot', c_slot)
        # Get sibling slots
        sibling_slots = []
        for slot in unit.get_prop('slots', []):
            if slot.startswith(c_slot) or c_slot.startswith(slot):
                sibling_slots.append(slot)
        new_unit.set_prop('c_slot_sibs', sibling_slots)
        new_unit.set_prop('not_for_real', True)
            
        # Update task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        context['task_results'] = task_results
        
        # Record application in h12
        h12 = rule.unit_registry.get_unit('h12')
        if h12:
            task = context.get('task', {})
            app = {
                'args': [task],
                'results': [new_unit],
                'credit': {'initial': 1.0},
                'description': [
                    "Will avoid",
                    c_slot, 
                    f"{', actually all of these: ' if len(sibling_slots) > 1 else ','}", 
                    sibling_slots if len(sibling_slots) > 1 else '',
                    "of units whenever finding",
                    g_slot,
                    "of them"
                ]
            }
            h12.add_to_prop('applications', app)
            
        # Add creditors for created unit
        creditors = ['h2']
        if task := context.get('task'):
            task_creditors = task.get('supplemental', {}).get('credit_to', [])
            creditors.extend(task_creditors)
        new_unit.set_prop('creditors', creditors)
            
        return True