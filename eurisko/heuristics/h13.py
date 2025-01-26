"""H13 heuristic implementation: Prevent mistakes based on object type."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h13(heuristic) -> None:
    """Configure H13: Form rules to prevent mistakes based on object type."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF C is about to die, then try to form a new heuristic, one which -- had it "
        "existed earlier -- would have prevented C from ever being defined in the first "
        "place, by preventing the kind of changed object from being changed")
    heuristic.set_prop('abbrev', "Form a rule that would have prevented this type of mistake")
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
        c_from = context.get('c_from')
        c_slot = context.get('c_slot')
        c_slot_sibs = context.get('c_slot_sibs', [])
        g_slot = context.get('g_slot')
        if not all([unit, c_from, c_slot, g_slot]):
            return False
            
        logger.info(f"\n\nJust before destroying a losing concept, Eurisko generalized "
                   f"from that bad experience in the following way: Eurisko will no "
                   f"longer alter the {c_from} inside any of these {c_slot_sibs if len(c_slot_sibs) > 1 else c_slot} "
                   f"slots of a unit when trying to find {g_slot} of that unit. "
                   f"We learned our lesson from {unit.name}\n")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Extract task and type information."""
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
            
        # Find task that created this unit
        creator_apps = creator.get_prop('applications', [])
        app = None
        for a in creator_apps:
            if a.get('results') and unit in a['results']:
                app = a
                break
                
        if not app:
            return False
            
        # Get task and transformation info
        task = app.get('task', {})
        transformations = app.get('description', [])
        if not task or not transformations:
            return False
            
        # Extract slot and type information
        c_slot = task.get('supplemental', {}).get('slot_to_change')
        g_slot = task.get('slot')
        
        # Find type transformation
        c_from = None
        c_to = None
        for trans in transformations:
            if isinstance(trans, dict) and '->' in trans:
                c_from = trans.get('from')
                c_to = trans.get('to')
                break
                
        if not all([c_slot, g_slot, c_from, c_to]):
            return False
            
        context.update({
            'c_slot': c_slot,
            'g_slot': g_slot,
            'c_from': c_from,
            'c_to': c_to
        })
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create preventative rule unit."""
        unit = context.get('unit')
        c_slot = context.get('c_slot')
        g_slot = context.get('g_slot')
        c_from = context.get('c_from')
        c_to = context.get('c_to')
        if not all([unit, c_slot, g_slot, c_from, c_to]):
            return False
            
        # Create new avoid rule
        new_unit = rule.unit_registry.create_unit('h-avoid-2')
        if not new_unit:
            return False
            
        # Set properties from context
        sibling_slots = []
        for slot in unit.get_prop('slots', []):
            if slot.startswith(c_slot) or c_slot.startswith(slot):
                sibling_slots.append(slot)
                
        props = {
            'g_slot': g_slot,
            'c_slot': c_slot,
            'c_slot_sibs': sibling_slots,
            'not_for_real': True,
            'c_from': c_from,
            'c_to': c_to
        }
        for k, v in props.items():
            new_unit.set_prop(k, v)
            
        # Update task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        context['task_results'] = task_results
        
        # Record application in h13
        h13 = rule.unit_registry.get_unit('h13')
        if h13:
            task = context.get('task', {})
            app = {
                'args': [task],
                'results': [new_unit],
                'credit': {'initial': 1.0},
                'description': [
                    "Will avoid changing a",
                    c_from,
                    "inside the",
                    c_slot,
                    f"{', actually all of these: ' if len(sibling_slots) > 1 else ','}", 
                    sibling_slots if len(sibling_slots) > 1 else '',
                    "of units whenever finding",
                    g_slot,
                    "of them"
                ]
            }
            h13.add_to_prop('applications', app)
            
        # Add creditors
        creditors = ['h13']
        if task := context.get('task'):
            task_creditors = task.get('supplemental', {}).get('credit_to', [])
            creditors.extend(task_creditors)
        new_unit.set_prop('creditors', creditors)
            
        return True