"""Core heuristic implementation for PyEurisko."""
from typing import Any, Dict, List, Optional, Set, Callable
import time
import logging
from copy import deepcopy
from .unit import Unit, UnitRegistry
from .slots import SlotRegistry

logger = logging.getLogger(__name__)

class Heuristic(Unit):
    """Base class for heuristic rules in Eurisko."""
    def __init__(self, name: str, description: str = "", worth: int = 700):
        """Initialize a heuristic with standard properties."""
        super().__init__(name, worth)
        self.set_prop('isa', ['heuristic'])
        self.set_prop('english', description)
        
        # Initialize tracking records
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
            # Each record tracks [total_time, num_calls]
            self.set_prop(record, [0.0, 0])
            # Failed records track unsuccessful attempts
            self.set_prop(f"{record}_failed", [0.0, 0])

    def is_potentially_relevant(self, context: Dict[str, Any]) -> bool:
        """Perform initial relevance check for this heuristic."""
        check_fn = self.get_prop('if_potentially_relevant')
        if not check_fn or not callable(check_fn):
            return False
            
        try:
            return bool(check_fn(context))
        except Exception as e:
            logger.error(f"Error in potential relevance check: {e}")
            return False

    def is_truly_relevant(self, context: Dict[str, Any]) -> bool:
        """Perform deeper relevance check."""
        check_fn = self.get_prop('if_truly_relevant')
        if not check_fn or not callable(check_fn):
            return True  # No deep check defined means implicitly relevant
            
        try:
            return bool(check_fn(context))
        except Exception as e:
            logger.error(f"Error in true relevance check: {e}")
            return False

    def is_subsumed_by(self, other_heuristic: 'Heuristic') -> bool:
        """Check if this heuristic is subsumed by another."""
        subsumers = self.get_prop('subsumed_by') or []
        return other_heuristic.name in subsumers

    def update_record(self, record_name: str, elapsed_time: float) -> None:
        """Update execution statistics for a record."""
        record = self.get_prop(record_name)
        if not record:
            record = [0.0, 0]
            
        record[0] += elapsed_time  # Total time
        record[1] += 1  # Number of executions
        self.set_prop(record_name, record)

    def apply(self, context: Dict[str, Any]) -> bool:
        """Apply this heuristic to the given context."""
        if not self.is_potentially_relevant(context):
            return False

        if not self.is_truly_relevant(context):
            return False

        start_time = time.time()
        success = True

        # Execute phases in sequence
        phases = [
            ('check_phase', 'if_parts'),
            ('print_phase', 'then_print_to_user'),
            ('compute_phase', 'then_compute'),
            ('conjecture_phase', 'then_conjecture'),
            ('define_phase', 'then_define_new_concepts')
        ]

        for phase_name, prop_name in phases:
            phase_fn = self.get_prop(prop_name)
            if callable(phase_fn):
                try:
                    phase_start = time.time()
                    if not phase_fn(context):
                        success = False
                        self.update_record(f"{prop_name}_failed", time.time() - phase_start)
                        break
                    self.update_record(prop_name, time.time() - phase_start)
                except Exception as e:
                    logger.error(f"Error in {phase_name}: {e}")
                    success = False
                    break

        # Record overall execution time
        elapsed = time.time() - start_time
        if success:
            self.update_record('overall_record', elapsed)
        else:
            self.update_record('overall_record_failed', elapsed)

        return success

class HeuristicRegistry:
    """Global registry for managing heuristic rules."""
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.unit_registry = UnitRegistry()
            cls._instance.initialize_core_heuristics()
        return cls._instance

    def initialize_core_heuristics(self) -> None:
        """Initialize the core set of heuristic rules."""
        core_rules = [
            # H1: Specialize sometimes-useful actions
            ('h1', "IF an op F has had some good applications, but over 4/5 are bad, "
                  "THEN conjecture that some specializations of F may be superior to F",
             724),
             
            # H2: Kill concepts that produce garbage
            ('h2', "IF you have just finished a task and some units were created, "
                  "AND one of the creators has a property of spewing garbage, "
                  "THEN reduce that creator's worth",
             700),
             
            # H3: Choose slot to specialize
            ('h3', "IF the current task is to specialize a unit, but no specific slot "
                  "to specialize is yet known, THEN randomly choose one",
             101),
             
            # H4: Gather data about new units
            ('h4', "IF a new unit has been synthesized, THEN place a task on the "
                  "agenda to gather new empirical data about it",
             703),
             
            # H5: Choose multiple slots to specialize
            ('h5', "IF the current task is to specialize a unit and no specific slot "
                  "has been chosen, THEN randomly select which slots to specialize",
             151)
        ]
        
        for name, desc, worth in core_rules:
            heuristic = Heuristic(name, desc, worth)
            self.unit_registry.register(heuristic)
            self._setup_heuristic(heuristic)

    def _setup_heuristic(self, heuristic: Heuristic) -> None:
        """Configure a specific heuristic's behavior."""
        if heuristic.name == 'h1':
            self._setup_h1(heuristic)
        elif heuristic.name == 'h2':
            self._setup_h2(heuristic)
        elif heuristic.name == 'h3':
            self._setup_h3(heuristic)
        elif heuristic.name == 'h4':
            self._setup_h4(heuristic)
        elif heuristic.name == 'h5':
            self._setup_h5(heuristic)

    def _setup_h1(self, h1: Heuristic) -> None:
        """Configure H1: Specialize sometimes-useful actions."""
        def check_applics(context: Dict[str, Any]) -> bool:
            """Check that unit has some recorded applications."""
            unit = context.get('unit')
            return bool(unit and unit.get_prop('applics'))
            
        def check_relevance(context: Dict[str, Any]) -> bool:
            """Check if unit has good and bad applications."""
            unit = context.get('unit')
            if not unit:
                return False
                
            applics = unit.get_prop('applics') or []
            if not applics:
                return False
                
            # Check if any applications have high worth 
            has_high_worth = any(app.get('worth', 0) > 800 
                               for app in applics)
            if not has_high_worth:
                return False
                
            # Calculate fraction of good applications
            good_count = sum(1 for app in applics 
                           if app.get('worth', 0) > 800)
            total_count = len(applics)
            return good_count / total_count < 0.2

        h1.set_prop('if_potentially_relevant', check_applics)
        h1.set_prop('if_truly_relevant', check_relevance)

    def _setup_h2(self, h2: Heuristic) -> None:
        """Configure H2: Kill concepts that produce garbage."""
        def check_task(context: Dict[str, Any]) -> bool:
            """Check for new units created by garbage producer."""
            task_results = context.get('task_results', {})
            if not task_results:
                return False
                
            new_units = task_results.get('new_units', [])
            if not new_units:
                return False
                
            creditors = set()
            for unit in new_units:
                creditors.update(unit.get_prop('creditors') or [])
            
            # Check for creditors that produce mostly useless units
            for creditor in creditors:
                creditor_unit = self.unit_registry.get_unit(creditor)
                if not creditor_unit:
                    continue
                    
                applics = creditor_unit.get_prop('applics') or []
                if len(applics) < 10:
                    continue
                    
                # Check if all applications produced units with no applics
                if all(app.get('result') and 
                      all(not unit.get_prop('applics')
                          for unit in app['result'])
                      for app in applics):
                    return True
                    
            return False
            
        h2.set_prop('if_finished_working_on_task', check_task)

    def _setup_h3(self, h3: Heuristic) -> None:
        """Configure H3: Choose slot to specialize."""
        def check_task(context: Dict[str, Any]) -> bool:
            """Check if we need to choose a slot to specialize."""
            unit = context.get('unit')
            task = context.get('task')
            if not unit or not task:
                return False
                
            return (task.get('task_type') == 'specialization' and
                    not task.get('slot_to_change'))

        h3.set_prop('if_working_on_task', check_task)

    def _setup_h4(self, h4: Heuristic) -> None:
        """Configure H4: Gather data about new units."""
        def check_task(context: Dict[str, Any]) -> bool:
            """Check for new units created."""
            task_results = context.get('task_results', {})
            return bool(task_results.get('new_units'))

        h4.set_prop('if_finished_working_on_task', check_task)

    def _setup_h5(self, h5: Heuristic) -> None:
        """Configure H5: Choose multiple slots to specialize."""
        def check_task(context: Dict[str, Any]) -> bool:
            """Check if we need to choose slots to specialize."""
            unit = context.get('unit')
            task = context.get('task')
            if not unit or not task:
                return False
                
            return (task.get('task_type') == 'specialization' and
                    not task.get('slots_to_change'))

        h5.set_prop('if_working_on_task', check_task)

    def get_applicable_heuristics(self, context: Dict[str, Any]) -> List[Heuristic]:
        """Find all heuristics that could apply to a context."""
        heuristics = []
        for unit_name in self.unit_registry.get_units_by_category('heuristic'):
            unit = self.unit_registry.get_unit(unit_name)
            if isinstance(unit, Heuristic) and unit.is_potentially_relevant(context):
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