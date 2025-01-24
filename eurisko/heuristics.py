"""Heuristic implementation for PyEurisko."""
from typing import Any, Dict, List, Optional, Callable
import logging
import time
from .unit import Unit, UnitRegistry

logger = logging.getLogger(__name__)

class Heuristic(Unit):
    """Represents a heuristic rule in the system."""

    def __init__(self, name: str, description: str = "", worth: int = 700):
        """Initialize a heuristic with default properties."""
        super().__init__(name, worth)
        self.set_prop('isa', ['heuristic'])
        self.set_prop('english', description)
        
        # Initialize tracking records
        self.initialize_records()

    def initialize_records(self):
        """Set up tracking records for the heuristic."""
        record_types = [
            'overall_record',
            'then_compute_record', 
            'then_print_record',
            'then_conjecture_record',
            'then_define_new_concepts_record'
        ]
        
        for record in record_types:
            # Each record is [total_time, num_calls]
            self.set_prop(record, [0.0, 0])
            # Failed records track unsuccessful attempts
            self.set_prop(f"{record}_failed", [0.0, 0])

    def is_relevant_to(self, context: Dict[str, Any]) -> bool:
        """Check if this heuristic is relevant to the current context."""
        # First check potential relevance
        check = self.get_prop('if_potentially_relevant')
        if not check or not callable(check):
            return False
            
        try:
            if not check(context):
                return False
        except Exception as e:
            logger.error(f"Error in potential relevance check: {e}")
            return False

        # Then check true relevance
        check = self.get_prop('if_truly_relevant')
        if not check or not callable(check):
            return True  # No true relevance check defined
            
        try:
            return bool(check(context))
        except Exception as e:
            logger.error(f"Error in true relevance check: {e}")
            return False

    def is_subsumed_by(self, other_heuristic: 'Heuristic') -> bool:
        """Check if this heuristic is subsumed by another."""
        subsumers = self.get_prop('subsumed_by') or []
        return other_heuristic.name in subsumers

    def apply(self, context: Dict[str, Any]) -> bool:
        """Apply this heuristic to the given context."""
        if not self.is_relevant_to(context):
            return False

        start_time = time.time()
        success = True

        # Execute phases in sequence
        phases = [
            ('pre_task_check', 'if_about_to_work_on_task'),
            ('main_task_work', 'if_working_on_task'),
            ('post_task_work', 'if_finished_working_on_task')
        ]

        for phase_name, prop_name in phases:
            phase_fn = self.get_prop(prop_name)
            if callable(phase_fn):
                try:
                    phase_start = time.time()
                    if not phase_fn(context):
                        success = False
                        self._update_record(f"{prop_name}_failed", time.time() - phase_start)
                        break
                    self._update_record(prop_name, time.time() - phase_start)
                except Exception as e:
                    logger.error(f"Error in {phase_name}: {e}")
                    success = False
                    break

        # Record overall execution time
        elapsed = time.time() - start_time
        if success:
            self._update_record('overall_record', elapsed)
        else:
            self._update_record('overall_record_failed', elapsed)

        return success

    def _update_record(self, record_name: str, elapsed_time: float) -> None:
        """Update execution statistics for a record."""
        record = self.get_prop(record_name)
        if not record:
            record = [0.0, 0]
            
        record[0] += elapsed_time  # Total time
        record[1] += 1  # Number of executions
        self.set_prop(record_name, record)

class HeuristicRegistry:
    """Manages the available heuristics in the system."""
    _instance = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.unit_registry = UnitRegistry()
            cls._instance.initialize_core_heuristics()
        return cls._instance

    def initialize_core_heuristics(self):
        """Initialize the core set of heuristics."""
        # H1: Specialize sometimes-useful actions
        h1 = Heuristic("h1", "IF an op F has had some good applications, but over 4/5 are bad, "
                            "THEN conjecture that some Specializations of F may be superior")
        h1.set_prop('worth', 724)
        h1.set_prop('if_potentially_relevant', lambda ctx: bool(ctx.get('applics')))
        h1.set_prop('if_truly_relevant', lambda ctx: self._h1_relevance_check(ctx))
        self.unit_registry.register(h1)

        # Add more core heuristics as needed
        self._register_core_rules()

    def _h1_relevance_check(self, context: Dict[str, Any]) -> bool:
        """Relevance check implementation for H1."""
        applics = context.get('applics', [])
        if not applics:
            return False
            
        # Check if any applications have high worth
        has_high_worth = any(application.get('worth', 0) > 800 
                           for application in applics)
        if not has_high_worth:
            return False
            
        # Calculate fraction of good applications
        good_count = sum(1 for app in applics if app.get('worth', 0) > 800)
        total_count = len(applics)
        
        return good_count / total_count < 0.2

    def _register_core_rules(self):
        """Register the core set of heuristic rules."""
        # This will be expanded as we implement more heuristics
        core_rules = []
        for rule in core_rules:
            self.unit_registry.register(rule)
            
    def get_applicable_heuristics(self, context: Dict[str, Any]) -> List[Heuristic]:
        """Find all heuristics that could apply to a context."""
        heuristics = []
        for unit_name in self.unit_registry.get_units_by_category('heuristic'):
            unit = self.unit_registry.get_unit(unit_name)
            if isinstance(unit, Heuristic) and unit.is_relevant_to(context):
                heuristics.append(unit)
        return heuristics

    def apply_heuristics(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply all relevant heuristics to a context."""
        results = []
        for heuristic in self.get_applicable_heuristics(context):
            start_time = time.time()
            success = heuristic.apply(context)
            elapsed = time.time() - start_time
            
            results.append({
                'heuristic': heuristic.name,
                'success': success,
                'elapsed': elapsed
            })
            
        return results