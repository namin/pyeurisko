"""H1 heuristic implementation: Specialize sometimes-useful actions."""
from typing import Any, Dict
from ..units import Unit
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h1(heuristic) -> None:
    """Configure H1: Specialize sometimes-useful actions."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 724)
    heuristic.set_prop('english', 
        "IF an op F (e.g., a mathematical function, a heuristic, etc.) has had some good "
        "applications, but over 4/5 are bad, THEN conjecture that some Specializations "
        "of F may be superior to F, and add tasks to specialize F to the Agenda.")
    heuristic.set_prop('abbrev', "Specialize a sometimes-useful action")
    
    # Initialize records as in LISP
    heuristic.set_prop('then_conjecture_record', (2393, 5))
    heuristic.set_prop('then_add_to_agenda_record', (377, 5))
    heuristic.set_prop('then_print_to_user_record', (2601, 5))
    heuristic.set_prop('overall_record', (7078, 5))
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check that unit has some recorded applications."""
        unit = context.get('unit')
        if not unit:
            return False
        applications = unit.get_prop('applications')
        return bool(applications)
        
    @rule_factory
    def if_truly_relevant(rule, context):
        """Check if unit has good and bad applications."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Get applications
        applications = unit.get_prop('applications')
        if not applications:
            return False
            
        # Count good vs total applications
        # In test case, each application is a dict with 'worth' directly
        total_count = len(applications)
        good_count = sum(1 for app in applications if app.get('worth', 0) >= 800)
        
        if total_count == 0:
            return False
            
        # Need at least one good application
        if good_count == 0:
            return False
            
        # Store fraction for use in conjecture
        fraction = good_count / total_count
        context['fraction'] = fraction
            
        # Check not subsumed
        if unit.get_prop('subsumed_by'):
            return False
            
        # More than 4/5 should be bad (i.e., fraction good < 0.2)
        return fraction <= 0.2

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of action to user."""
        unit = context.get('unit')
        conjec = context.get('conjecture')
        if not unit or not conjec:
            return False
            
        logger.info(f"\n{conjec}:\nSince some specializations of {unit.name} are quite "
                   f"valuable, but over four-fifths are trash, EURISKO has recognized "
                   f"the value of finding new concepts similar to -- but more specialized "
                   f"than -- {unit.name}, and (to that end) has added a new task to the "
                   f"agenda to find such specializations.")
        return True

    @rule_factory
    def then_conjecture(rule, context):
        """Create conjecture about specializing the unit."""
        unit = context.get('unit')
        system = context.get('system')
        fraction = context.get('fraction', 0)
        
        if not unit or not system:
            return False
        
        # Create new conjecture
        conjec_name = system.new_name('conjec')
        conjec = system.create_unit(conjec_name, 'proto-conjec')
        if not conjec:
            return False
        
        english = (f"Specializations of {unit.name} may be more useful than it is, "
                  f"since it has some good instances but many more poor ones. "
                  f"({(1.0 - fraction)*100:.1f}% are losers)")
        
        conjec.set_prop('english', english)
        conjec.set_prop('abbrev', 
            f"{unit.name} sometimes wins, usually loses, so specializations may win big")
        
        # Calculate worth based on fraction and average worths
        worth = int(min(1000, (0.9 - fraction) * 1000))
        conjec.set_prop('worth', worth)
        
        # Add to conjectures list
        if not system.add_conjecture(conjec):
            return False
            
        context['conjecture'] = conjec
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add task to specialize the unit."""
        unit = context.get('unit')
        system = context.get('system')
        conjec = context.get('conjecture')
        
        if not all([unit, system, conjec]):
            return False
        
        # Create specialization task
        task = {
            'priority': unit.get_prop('worth', 500),
            'unit': unit,
            'slot': 'specializations', 
            'reasons': [conjec],
            'supplemental': {
                'credit_to': ['h1'],
                'task_type': 'specialization'
            }
        }
        
        if not system.task_manager.add_task(task):
            return False
            
        system.add_task_result('new_tasks', "1 unit must be specialized")
        return True