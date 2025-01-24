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
            ('if_parts', 'Checking conditions'),
            ('then_print_to_user', 'Printing output'),
            ('then_compute', 'Computing results'),
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
                if not result:
                    logger.debug(f"Phase {phase_name} failed for {self.name}")
                    self.update_record(f"{phase_name}_failed", time.time() - phase_start)
                    return False
                self.update_record(phase_name, time.time() - phase_start)
            except Exception as e:
                logger.error(f"Error in {description} phase of {self.name}: {e}")
                self.update_record(f"{phase_name}_failed", time.time() - phase_start)
                return False

        return True


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
                
            # Analyze application worth distribution
            good_count = 0
            total_count = 0
            for app in applics:
                if isinstance(app, dict):
                    worth = app.get('worth', 0)
                    if worth > 800:
                        good_count += 1
                    total_count += 1
                    
            if total_count == 0:
                return False
                
            # Need at least one good application but mostly bad ones
            ratio = good_count / total_count
            return good_count > 0 and ratio < 0.2

        def compute_action(context: Dict[str, Any]) -> bool:
            """Execute H1's action."""
            unit = context.get('unit')
            if not unit:
                return False
                
            unit.set_prop('needs_specialization', True)
            return True

        h1.set_prop('if_potentially_relevant', check_applics)
        h1.set_prop('if_truly_relevant', check_relevance)
        h1.set_prop('then_compute', compute_action)

    def _setup_h2(self, h2: Heuristic) -> None:
        """Configure H2: Kill concepts that produce garbage."""
        def check_task(context: Dict[str, Any]) -> bool:
            """Check for new units from garbage producers."""
            task_results = context.get('task_results', {})
            if not task_results:
                return False
                
            new_units = task_results.get('new_units', [])
            if not new_units:
                return False
                
            for unit in new_units:
                if not isinstance(unit, Unit):
                    continue
                    
                creditors = unit.get_prop('creditors') or []
                for creditor in creditors:
                    creditor_unit = self.unit_registry.get_unit(creditor)
                    if not creditor_unit:
                        continue
                        
                    applics = creditor_unit.get_prop('applics') or []
                    if len(applics) >= 10:
                        # Check if all results lack applications
                        if all(isinstance(app, dict) and
                              all(not hasattr(u, 'get_prop') or not u.get_prop('applics')
                                  for u in app.get('result', []))
                              for app in applics):
                            return True
                            
            return False
            
        def reduce_worth(context: Dict[str, Any]) -> bool:
            """Reduce worth of garbage-producing units."""
            task_results = context.get('task_results', {})
            new_units = task_results.get('new_units', [])
            
            reduced = False
            for unit in new_units:
                if isinstance(unit, Unit):
                    for creditor in unit.get_prop('creditors') or []:
                        creditor_unit = self.unit_registry.get_unit(creditor)
                        if creditor_unit:
                            current_worth = creditor_unit.worth_value()
                            creditor_unit.set_prop('worth', current_worth // 2)
                            reduced = True
                            
            return reduced

        h2.set_prop('if_finished_working_on_task', check_task)
        h2.set_prop('then_compute', reduce_worth)

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
            new_units = task_results.get('new_units', [])
            return bool(new_units and isinstance(new_units, list))

        def schedule_analysis(context: Dict[str, Any]) -> bool:
            """Schedule analysis tasks for new units."""
            task_results = context.get('task_results', {})
            new_units = task_results.get('new_units', [])
            
            if not new_units:
                return False
                
            for unit in new_units:
                if isinstance(unit, Unit):
                    unit.set_prop('needs_analysis', True)
            return True

        h4.set_prop('if_finished_working_on_task', check_task)
        h4.set_prop('then_compute', schedule_analysis)

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