"""H21 heuristic implementation: Find extensions of operations."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h21(heuristic) -> None:
    """Configure H21: Identify operation extensions."""
    heuristic.set_prop('worth', 400)
    heuristic.set_prop('english', "IF an op u duplicates all the results of u2, THEN conjecture that u is an extension of u2")
    heuristic.set_prop('abbrev', "See if u is an extension of u2")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_conjecture', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we're looking for conjectures."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]) or task.get('slot') != 'conjectures':
            return False
            
        involved_units = task.get('supplemental', {}).get('involved_units', [])
        context['involved_units'] = involved_units
        return bool(involved_units)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print extension discovery."""
        unit = context.get('unit')
        result_units = context.get('result_units', [])
        if not all([unit, result_units]):
            return False
            
        logger.info(f"\nApparently {unit.name} is an extension of {result_units}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Find potential extensions."""
        unit = context.get('unit')
        involved_units = context.get('involved_units')
        if not all([unit, involved_units]):
            return False
            
        result_units = []
        for other_name in involved_units:
            other = rule.unit_registry.get_unit(other_name)
            if not other or not other.get_prop('applications'):
                continue
                
            other_apps = other.get_prop('applications', [])
            unit_apps = unit.get_prop('applications', [])
            
            if all(any(o_app.get('args') == u_app.get('args') 
                      for u_app in unit_apps)
                   for o_app in other_apps):
                result_units.append(other_name)
                
        context['result_units'] = result_units
        return bool(result_units)

    @rule_factory
    def then_conjecture(rule, context):
        """Create conjectures about extensions."""
        unit = context.get('unit')
        result_units = context.get('result_units')
        if not all([unit, result_units]):
            return False
            
        system = rule.unit_registry
        
        for other_name in result_units:
            other = system.get_unit(other_name)
            if not other:
                continue
                
            # Create conjecture
            conjec_name = system.new_name('conjec')
            conjec = system.create_unit(conjec_name, 'proto-conjec')
            if not conjec:
                continue
                
            # Set properties
            conjec.set_prop('english', 
                f"All applications of {other_name} are also applications of "
                f"{unit.name}, so we presume that {unit.name} is an extension "
                f"of {other_name}")
            conjec.set_prop('abbrev', 
                f"{unit.name} appears to be an extension of {other_name}")
                
            # Calculate worth
            base_worth = (unit.worth_value() + other.worth_value() + 
                        rule.worth_value()) // 3
            app_count = len(other.get_prop('applications', []))
            conjec.set_prop('worth', min(1000, base_worth + min(app_count * 100, 500)))
            
            # Set relationships
            conjec.set_prop('conjecture_about', [unit.name, other_name])
            
            # Add to collections
            if not system.add_conjecture(conjec):
                continue
                
            # Update unit relationships
            other.add_to_prop('conjectures', conjec_name)
            unit.add_to_prop('conjectures', conjec_name)
            unit.add_to_prop('restrictions', other_name)
            other.add_to_prop('extensions', unit.name)
            
        return True