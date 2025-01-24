"""H1 heuristic implementation: Specialize sometimes-useful actions."""
from typing import Any, Dict
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h1(heuristic) -> None:
    """Configure H1: Specialize sometimes-useful actions."""
    def check_applics(context: Dict[str, Any]) -> bool:
        """Check that unit has some recorded applications."""
        unit = context.get('unit')
        if not unit:
            return False
        applics = unit.get_prop('applics')
        return bool(applics)
        
    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit has good and bad applications."""
        unit = context.get('unit')
        if not unit:
            return False
            
        applics = unit.get_prop('applics') or []
        if not applics:
            return False
            
        # Count applications by worth
        total_count = 0
        good_count = 0
        for app in applics:
            if not isinstance(app, dict):
                continue
            worth = app.get('worth', 0)
            if worth >= 800:  # Good applications are those worth >= 800
                good_count += 1
            total_count += 1

        # Need at least one good application but more than 4/5 should be bad
        result = good_count > 0 and total_count > 0 and (good_count / total_count) <= 0.2
        
        if not result:
            logger.debug(f"H1 relevance check failed: good_count={good_count}, total_count={total_count}, ratio={good_count/total_count if total_count else 0}")
            
        return result

    def compute_action(context: Dict[str, Any]) -> bool:
        """Execute H1's action."""
        unit = context.get('unit')
        if not unit:
            return False
            
        unit.set_prop('needs_specialization', True)
        return True

    heuristic.set_prop('if_potentially_relevant', check_applics)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_compute', compute_action)