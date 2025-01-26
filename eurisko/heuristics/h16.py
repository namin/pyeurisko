"""H16 heuristic implementation: Generalize useful actions."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h16(heuristic) -> None:
    """Configure H16: Generalize a sometimes-useful action."""
    heuristic.set_prop('worth', 600)
    heuristic.set_prop('english', 
        "IF the results of performing f are sometimes (at least one time in ten) useful, "
        "THEN consider creating new generalizations of f")
    heuristic.set_prop('abbrev', "Generalize a sometimes-useful action")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_conjecture', 'then_add_to_agenda', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check if unit has applications."""
        unit = context.get('unit')
        if not unit:
            return False
        return bool(unit.get_prop('applications'))

    @rule_factory
    def if_truly_relevant(rule, context):
        """Check if worth exceeds threshold."""
        unit = context.get('unit')
        if not unit:
            return False
            
        applications = unit.get_prop('applications', [])
        high_worth_count = 0
        total_count = 0
        
        for app in applications:
            results = app.get('results', [])
            for result in results:
                total_count += 1
                if result and result.get_prop('worth', 0) >= 800:
                    high_worth_count += 1
                    
        if total_count == 0:
            return False
            
        fraction = high_worth_count / total_count
        context['fraction'] = fraction
        
        # Check generalization criteria
        return (fraction > 0.1 and 
                not unit.get_prop('subsumed_by'))

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of generalization."""
        unit = context.get('unit')
        conjec = context.get('conjecture')
        if not all([unit, conjec]):
            return False
            
        logger.info(f"\n{conjec}:\nSince some applications of {unit.name} are very "
                   f"valuable, EURISKO wants to find new concepts which are slightly "
                   f"more generalized than {unit.name}, and (to that end) has added "
                   f"a new task to the agenda to find such concepts.")
        return True

    @rule_factory
    def then_conjecture(rule, context):
        """Create conjecture about generalization."""
        unit = context.get('unit')
        fraction = context.get('fraction')
        if not all([unit, fraction is not None]):
            return False
            
        # Create new conjecture unit
        system = rule.unit_registry
        conjec_name = system.new_name('conjec')
        conjec = system.create_unit(conjec_name, 'proto-conjec')
        if not conjec:
            return False
            
        # Set properties
        description = f"Generalizations of {unit.name} may be very valuable in the " \
                     f"long run, since it already has some good applications " \
                     f"({fraction*100:.1f}% are winners)"
        conjec.set_prop('english', description)
        conjec.set_prop('abbrev', 
            f"{unit.name} sometimes wins, so generalizations of it may be very big winners")
        
        # Calculate worth based on unit and h16
        h16_worth = rule.worth_value()
        unit_worth = unit.worth_value()
        conjec.set_prop('worth', (h16_worth + unit_worth) // 2)
        
        # Add to conjectures
        if not system.add_conjecture(conjec):
            return False
            
        context['conjecture'] = conjec
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add task to generalize the unit."""
        unit = context.get('unit')
        conjec = context.get('conjecture')
        system = rule.unit_registry
        
        if not all([unit, conjec, system]):
            return False
            
        # Create generalization task
        task = {
            'priority': (unit.worth_value() + rule.worth_value()) // 2,
            'unit': unit,
            'slot': 'generalizations',
            'reasons': [conjec],
            'supplemental': {
                'credit_to': ['h16']
            }
        }
        
        if not system.task_manager.add_task(task):
            return False
            
        system.add_task_result('new_tasks', "1 unit must be generalized")
        return True