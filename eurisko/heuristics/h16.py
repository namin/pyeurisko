"""H16 heuristic implementation: Generalize moderately successful actions."""
from typing import Any, Dict, Optional
from ..unit import Unit
import logging
import math

logger = logging.getLogger(__name__)

def setup_h16(heuristic) -> None:
    """Configure H16: Generalize moderately successful actions.
    
    This heuristic looks for concepts that have shown consistent success
    (>10% high-worth applications) and suggests exploring generalizations.
    """
    # Set core properties from original Eurisko
    heuristic.set_prop('worth', 600)
    heuristic.set_prop('english',
        "IF an op F has shown significant success (more than 1 in 10 applications "
        "are valuable), THEN conjecture that some Generalizations of F may be even "
        "more valuable, and add tasks to generalize F to the Agenda.")
    heuristic.set_prop('abbrev', "Generalize a consistently-useful action")
    
    # Initialize success tracking
    heuristic.set_prop('then_conjecture_record', (653, 4))
    heuristic.set_prop('then_add_to_agenda_record', (90, 4)) 
    heuristic.set_prop('then_print_to_user_record', (622, 4))
    heuristic.set_prop('overall_record', (1756, 4))
    heuristic.set_prop('arity', 1)

    def check_applics(context: Dict[str, Any]) -> bool:
        """Verify unit has recorded applications."""
        unit = context.get('unit')
        if not unit:
            return False
        alg = unit.get_prop('alg')  # Check if unit has algorithm
        return bool(alg and unit.get_prop('applics'))

    def analyze_worth_distribution(applics) -> Dict[str, float]:
        """Analyze the distribution of worth values in applications.
        
        Returns:
            Dict with:
            - success_ratio: Fraction of high-worth applications
            - avg_worth: Average worth across all applications 
            - worth_variance: Variance in worth values
        """
        if not applics:
            return {'success_ratio': 0, 'avg_worth': 0, 'worth_variance': 0}
            
        worth_values = [app.get('worth', 0) for app in applics]
        high_worth = sum(1 for w in worth_values if w >= 800)
        
        avg = sum(worth_values) / len(worth_values)
        variance = sum((w - avg) ** 2 for w in worth_values) / len(worth_values)
        
        return {
            'success_ratio': high_worth / len(applics),
            'avg_worth': avg,
            'worth_variance': variance
        }

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit demonstrates consistent moderate success."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Get and validate applications
        applics = unit.get_prop('applics')
        if not applics:
            return False
            
        # Full worth analysis
        worth_stats = analyze_worth_distribution(applics)
        context['worth_stats'] = worth_stats
            
        # Need >10% success rate but not too high to avoid overgeneralization
        success_ratio = worth_stats['success_ratio']
        if not (0.1 < success_ratio < 0.8):
            return False
            
        # Check not already subsumed
        if unit.get_prop('subsumed_by'):
            return False
            
        return True

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Print explanation of generalization opportunity."""
        unit = context.get('unit')
        conjec = context.get('conjecture')
        worth_stats = context.get('worth_stats', {})
        
        if not all([unit, conjec, worth_stats]):
            return False
            
        success_pct = worth_stats['success_ratio'] * 100
        logger.info(
            f"\n{conjec}:\n"
            f"Since {unit.name} shows consistent success ({success_pct:.1f}% valuable "
            f"applications), EURISKO sees potential value in finding concepts that "
            f"generalize {unit.name}. A new task has been added to explore such "
            f"generalizations."
        )
        return True

    def make_conjecture(context: Dict[str, Any]) -> bool:
        """Create conjecture about generalizing the unit."""
        unit = context.get('unit')
        system = context.get('system')
        worth_stats = context.get('worth_stats', {})
        
        if not all([unit, system, worth_stats]):
            return False
            
        conjec_name = system.new_name('conjec')
        conjec = system.create_unit(conjec_name, 'proto-conjec')
        
        success_pct = worth_stats['success_ratio'] * 100
        english = (
            f"Generalizations of {unit.name} may be valuable in the long run, as it "
            f"already shows consistent success ({success_pct:.1f}% of applications "
            f"are valuable) with average worth {worth_stats['avg_worth']:.1f}"
        )
        
        conjec.set_prop('english', english)
        conjec.set_prop('abbrev',
            f"{unit.name} wins {success_pct:.1f}% of the time - generalizations may win more")
        
        # Worth based on success rate and consistency
        base_worth = 600  # H16's base worth
        consistency_bonus = math.exp(-worth_stats['worth_variance'] / 1000) * 200
        worth = int(min(1000, base_worth * worth_stats['success_ratio'] + consistency_bonus))
        
        conjec.set_prop('worth', worth)
        system.add_conjecture(conjec)
        context['conjecture'] = conjec
        return True

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add task to explore generalizations."""
        unit = context.get('unit')
        system = context.get('system')
        conjec = context.get('conjecture')
        worth_stats = context.get('worth_stats', {})
        
        if not all([unit, system, conjec, worth_stats]):
            return False
            
        # Calculate priority based on unit worth and success metrics
        priority = int(
            unit.get_prop('worth', 500) * 
            (0.5 + worth_stats['success_ratio']) *
            math.exp(-worth_stats['worth_variance'] / 1000)
        )
        
        task = {
            'priority': priority,
            'unit': unit,
            'slot': 'generalizations',
            'reasons': [conjec],
            'supplemental': {
                'credit_to': ['h16'],
                'task_type': 'generalization',
                'worth_stats': worth_stats
            }
        }
        
        system.task_manager.add_task(task)
        system.add_task_result('new_tasks', "1 unit will be explored for generalizations")
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_applics)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_conjecture', make_conjecture)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)