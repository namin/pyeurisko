"""H21 heuristic implementation: Identify extension relationships between operations."""
from typing import Any, Dict, List, Set
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h21(heuristic) -> None:
    """Configure H21: Detect when one operation extends another.
    
    This heuristic examines operation pairs to identify when one operation's
    behavior completely encompasses another's, indicating a potential extension
    relationship. These relationships help build the hierarchical understanding
    of operations in the system.
    """
    heuristic.set_prop('worth', 400)
    heuristic.set_prop('english',
        "IF an operation U duplicates all the results of U2, THEN conjecture "
        "that U is an extension of U2.")
    heuristic.set_prop('abbrev', "See if U is an extension of U2")
    
    # Initialize record keeping
    heuristic.set_prop('then_compute_failed_record', (805, 18))
    heuristic.set_prop('then_compute_record', (3584, 2))
    heuristic.set_prop('then_conjecture_record', (3055, 2))
    heuristic.set_prop('then_print_to_user_record', (287, 2))
    heuristic.set_prop('overall_record', (11576, 2))
    heuristic.set_prop('arity', 1)

    def check_task_relevance(context: Dict[str, Any]) -> bool:
        """Verify task is examining conjectures with involved units."""
        task = context.get('task')
        if not task:
            return False
            
        slot = task.get('slot')
        if slot != 'conjectures':
            return False
            
        involved_units = task.get('supplemental', {}).get('involved_units', [])
        if not involved_units:
            return False
            
        context['involved_units'] = involved_units
        return True

    def analyze_application_overlap(unit: Unit, other: Unit) -> Dict[str, Any]:
        """Analyze how one unit's applications relate to another's.
        
        Returns a dictionary containing:
        - fully_contains: Whether unit contains all of other's applications 
        - overlap_ratio: Fraction of shared applications
        - unique_results: Results unique to unit
        """
        unit_apps = unit.get_prop('applications', [])
        other_apps = other.get_prop('applications', [])
        
        # Convert to sets for comparison
        unit_results = {
            tuple(app['args']): app['result']
            for app in unit_apps
        }
        other_results = {
            tuple(app['args']): app['result']
            for app in other_apps
        }
        
        # Find overlapping applications
        shared_args = set(unit_results.keys()) & set(other_results.keys())
        matching_results = sum(
            1 for args in shared_args
            if unit_results[args] == other_results[args]
        )
        
        return {
            'fully_contains': (
                matching_results == len(other_results) and
                len(unit_results) > len(other_results)
            ),
            'overlap_ratio': (
                matching_results / len(other_results)
                if other_results else 0
            ),
            'unique_results': len(unit_results) - matching_results
        }

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report discovered extension relationships."""
        unit = context.get('unit')
        extensions = context.get('extensions', [])
        
        if not unit or not extensions:
            return False
            
        for ext in extensions:
            logger.info(
                f"\n{unit.name} appears to be an extension of {ext['unit'].name} "
                f"(contains all results plus {ext['unique']} unique results)"
            )
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Identify potential extension relationships."""
        unit = context.get('unit')
        system = context.get('system')
        involved_units = context.get('involved_units', [])
        
        if not all([unit, system, involved_units]):
            return False
            
        extensions = []
        for other_name in involved_units:
            other = system.unit_registry.get_unit(other_name)
            if not other:
                continue
                
            overlap = analyze_application_overlap(unit, other)
            if overlap['fully_contains']:
                extensions.append({
                    'unit': other,
                    'overlap': overlap['overlap_ratio'],
                    'unique': overlap['unique_results']
                })
                
        context['extensions'] = extensions
        return bool(extensions)

    def make_conjecture(context: Dict[str, Any]) -> bool:
        """Create conjectures about extension relationships."""
        unit = context.get('unit')
        system = context.get('system')
        extensions = context.get('extensions', [])
        
        if not all([unit, system, extensions]):
            return False
            
        for ext in extensions:
            other = ext['unit']
            
            # Create the conjecture
            conjec_name = system.new_name('conjec')
            conjec = system.create_unit(conjec_name, 'proto-conjec')
            
            english = (
                f"All applications of {other.name} are also applications of "
                f"{unit.name}, suggesting that {unit.name} is an extension of "
                f"{other.name}. {unit.name} also has {ext['unique']} unique "
                f"applications not covered by {other.name}."
            )
            
            conjec.set_prop('english', english)
            conjec.set_prop('abbrev', 
                f"{unit.name} appears to be an extension of {other.name}")
            
            # Worth based on overlap and uniqueness
            worth = int(min(1000, (
                400 * ext['overlap'] +  # Reward completeness of overlap
                200 * (ext['unique'] / len(unit.get_prop('applications', []))) +  # Reward uniqueness
                200  # Base worth
            )))
            conjec.set_prop('worth', worth)
            
            # Record the relationship
            conjec.set_prop('conjecture_about', [unit.name, other.name])
            
            # Add conjecture to both units
            system.add_conjecture(conjec)
            unit.add_to_prop('conjectures', conjec.name)
            other.add_to_prop('conjectures', conjec.name)
            
            # Update relationship tracking
            unit.add_to_prop('restrictions', other.name)
            other.add_to_prop('extensions', unit.name)
            
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_working_on_task', check_task_relevance)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_conjecture', make_conjecture)
