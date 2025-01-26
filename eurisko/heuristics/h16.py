"""H16 heuristic implementation: Generalize moderately successful actions."""
from typing import Any, Dict, Optional
from ..units import Unit
import logging
import math
from ..heuristics import rule_factory

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

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Verify unit has recorded applications."""
        unit = context.get('unit')
        if not unit:
            return False
        alg = unit.get_prop('alg')  # Check if unit has algorithm
        return bool(alg and unit.get_prop('applications'))

    @rule_factory
    def if_truly_relevant(rule, context):
        """Check if unit demonstrates consistent moderate success."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Get and validate applications
        applications = unit.get_prop('applications')
        if not applications:
            return False
            
        # Analyze worth distribution
        worth_values = [app.get('worth', 0) for app in applications]
        high_worth = sum(1 for w in worth_values if w >= 800)
        
        if not worth_values:
            return False
            
        avg = sum(worth_values) / len(worth_values)
        variance = sum((w - avg) ** 2 for w in worth_values) / len(worth_values)
        
        worth_stats = {
            'success_ratio': high_worth / len(applications),
            'avg_worth': avg,
            'worth_variance': variance
        }
        
        context['worth_stats'] = worth_stats
            
        # Need >10% success rate but not too high to avoid overgeneralization
        success_ratio = worth_stats['success_ratio']
        if not (0.1 < success_ratio < 0.8):
            return False
            
        # Check not already subsumed
        if unit.get_prop('subsumed_by'):
            return False
            
        return True

    @rule_factory
    def then_print_to_user(rule, context):
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

    @rule_factory
    def then_conjecture(rule, context):
        """Create conjecture about generalizing the unit."""
        unit = context.get('unit')
        worth_stats = context.get('worth_stats', {})
        
        if not all([unit, worth_stats]):
            return False
            
        # Create new conjecture unit
        conjec_name = f"conjec_{unit.name}_generalization"
        conjec = rule.unit_registry.create_unit(conjec_name)
        if not conjec:
            return False
            
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
        conjec.set_prop('isa', ['proto-conjec'])
        
        rule.unit_registry.register(conjec)
        context['conjecture'] = conjec
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add task to explore generalizations."""
        unit = context.get('unit')
        conjec = context.get('conjecture')
        worth_stats = context.get('worth_stats', {})
        
        if not all([unit, conjec, worth_stats]):
            return False
            
        # Calculate priority based on unit worth and success metrics
        priority = int(
            unit.get_prop('worth', 500) * 
            (0.5 + worth_stats['success_ratio']) *
            math.exp(-worth_stats['worth_variance'] / 1000)
        )
        
        task = {
            'priority': priority,
            'unit': unit.name,
            'slot': 'generalizations',
            'reasons': [conjec.name],
            'supplemental': {
                'credit_to': ['h16'],
                'task_type': 'generalization',
                'worth_stats': worth_stats
            }
        }
        
        if not rule.task_manager.add_task(task):
            return False
            
        context['task_results'] = {
            'new_tasks': "1 unit will be explored for generalizations"
        }
        return True