"""H14 heuristic implementation: Prevent specific types of replacements."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h14(heuristic) -> None:
    """Configure H14: Form rules to prevent specific replacements."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF C is about to die, then try to form a new heuristic that would have prevented "
        "the same losing sort of entity being the replacer")
    heuristic.set_prop('abbrev', "Form a rule that would have prevented this type of replacement")
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
        c_to = context.get('c_to')
        c_slot = context.get('c_slot')
        c_slot_sibs = context.get('c_slot_sibs', [])
        g_slot = context.get('g_slot')
        if not all([unit, c_to, c_slot, g_slot]):
            return False
            
        logger.info(f"\n\nJust before destroying a losing concept, Eurisko generalized "
                   f"from that bad experience, in the following way: Eurisko will no "
                   f"longer change something into {c_to} inside any of these "
                   f"{c_slot_sibs if len(c_slot_sibs) > 1 else c_slot} slots of a unit when trying "
                   f"to find {g_slot} of that unit. We learned our lesson from {unit.name}\n")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Extract task and replacement information."""
        unit = context.get('unit')
        if not unit:
            return False
            
        creditors = unit.get_prop('creditors', [])
        if not creditors:
            return False
            
        creator = rule.unit_registry.get_unit(creditors[0])
        if not creator:
            return False
            
        creator_apps = creator.get_prop('applications', [])
        app = None
        for a in creator_apps:
            if a.get('results') and unit in a['results']:
                app = a
                break
                
        if not app:
            return False
            
        task = app.get('task', {})
        transformations = app.get('description', [])
        if not task or not transformations:
            return False
            
        c_slot = task.get('supplemental', {}).get('slot_to_change')
        g_slot = task.get('slot')
        
        c_to = None
        for trans in transformations:
            if isinstance(trans, dict) and '->' in trans:
                c_to = trans.get('to')
                break
                
        if not all([c_slot, g_slot, c_to]):
            return False
            
        context.update({
            'c_slot': c_slot,
            'g_slot': g_slot,
            'c_to': c_to
        })
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create preventative rule unit."""
        unit = context.get('unit')
        c_slot = context.get('c_slot')
        g_slot = context.get('g_slot')
        c_to = context.get('c_to')
        if not all([unit, c_slot, g_slot, c_to]):
            return False
            
        new_unit = rule.unit_registry.create_unit('h-avoid-3')
        if not new_unit:
            return False
            
        sibling_slots = []
        for slot in unit.get_prop('slots', []):
            if slot.startswith(c_slot) or c_slot.startswith(slot):
                sibling_slots.append(slot)
                
        props = {
            'g_slot': g_slot,
            'c_slot': c_slot,
            'c_slot_sibs': sibling_slots,
            'not_for_real': True,
            'c_to': c_to
        }
        for k, v in props.items():
            new_unit.set_prop(k, v)
            
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        context['task_results'] = task_results
        
        h14 = rule.unit_registry.get_unit('h14')
        if h14:
            task = context.get('task', {})
            app = {
                'args': [task],
                'results': [new_unit],
                'credit': {'initial': 1.0},
                'description': [
                    "Will avoid changing anything into a",
                    c_to,
                    "inside the",
                    c_slot,
                    f"{', actually all of these: ' if len(sibling_slots) > 1 else ','}", 
                    sibling_slots if len(sibling_slots) > 1 else '',
                    "of units whenever finding",
                    g_slot,
                    "of them"
                ]
            }
            h14.add_to_prop('applications', app)
            
        creditors = ['h14']
        if task := context.get('task'):
            task_creditors = task.get('supplemental', {}).get('credit_to', [])
            creditors.extend(task_creditors) 
        new_unit.set_prop('creditors', creditors)
            
        return True