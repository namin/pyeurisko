"""Base heuristic class implementation."""
from typing import Any, Dict, List, Optional, Set, Callable
import time
import logging
from copy import deepcopy
from ..unit import Unit

logger = logging.getLogger(__name__)

class Heuristic(Unit):
    """Base class for heuristic rules in Eurisko."""
    def __init__(self, name: str, description: str = "", worth: int = 700):
        """Initialize a heuristic with standard properties."""
        super().__init__(name, worth)
        self.set_prop('isa', ['heuristic'])
        self.set_prop('english', description)
        self.initialize_records()

    def initialize_records(self) -> None:
        """Set up performance tracking records."""
        record_types = [
            'overall_record',
            'then_compute_record',
            'then_print_record',
            'then_conjecture_record',
            'then_define_new_concepts_record'
        ]
        
        for record in record_types:
            self.set_prop(record, [0.0, 0])
            self.set_prop(f"{record}_failed", [0.0, 0])

    def is_potentially_relevant(self, context: Dict[str, Any]) -> bool:
        """Perform initial relevance check for this heuristic."""
        check_fn = self.get_prop('if_potentially_relevant')
        if not check_fn or not callable(check_fn):
            return True
            
        try:
            result = check_fn(context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error in potential relevance check for {self.name}: {e}")
            return False

    def is_truly_relevant(self, context: Dict[str, Any]) -> bool:
        """Perform deeper relevance check."""
        check_fn = self.get_prop('if_truly_relevant')
        if not check_fn or not callable(check_fn):
            return True
            
        try:
            result = check_fn(context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error in true relevance check for {self.name}: {e}")
            return False

    def is_subsumed_by(self, other_heuristic: 'Heuristic') -> bool:
        """Check if this heuristic is subsumed by another."""
        subsumers = self.get_prop('subsumed_by') or []
        return other_heuristic.name in subsumers

    def update_record(self, record_name: str, elapsed_time: float) -> None:
        """Update execution statistics for a record."""
        record = list(self.get_prop(record_name) or [0.0, 0])
        record[0] += elapsed_time  # Total time
        record[1] += 1  # Number of executions
        self.set_prop(record_name, record)

    def apply(self, context: Dict[str, Any]) -> bool:
        """Apply this heuristic to the given context."""
        if not self.is_potentially_relevant(context):
            logger.debug(f"Heuristic {self.name} not potentially relevant")
            return False

        if not self.is_truly_relevant(context):
            logger.debug(f"Heuristic {self.name} not truly relevant")
            return False

        start_time = time.time()
        try:
            success = self._execute_phases(context)
        except Exception as e:
            logger.error(f"Error executing heuristic {self.name}: {e}")
            success = False

        # Record execution time
        elapsed = time.time() - start_time
        self.update_record('overall_record' if success else 'overall_record_failed', elapsed)

        return success

    def _execute_phases(self, context: Dict[str, Any]) -> bool:
        """Execute all phases of the heuristic."""
        phases = [
            ('then_compute', 'Computing results'),
            ('then_print', 'Printing output'),
            ('then_conjecture', 'Making conjectures'),
            ('then_define_new_concepts', 'Defining concepts')
        ]

        for phase_name, description in phases:
            phase_fn = self.get_prop(phase_name)
            if not phase_fn or not callable(phase_fn):
                continue

            phase_start = time.time()
            try:
                result = phase_fn(context)
                if result is False:  # Only treat explicit False as failure
                    logger.debug(f"Phase {phase_name} failed for {self.name}")
                    self.update_record(f"{phase_name}_record_failed", time.time() - phase_start)
                    return False
                self.update_record(f"{phase_name}_record", time.time() - phase_start)
            except Exception as e:
                logger.error(f"Error in {description} phase of {self.name}: {e}")
                self.update_record(f"{phase_name}_record_failed", time.time() - phase_start)
                return False

        return True