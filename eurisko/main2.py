"""Main entry point for PyEurisko with enhanced task and heuristic management."""

from func_timeout import func_timeout, FunctionTimedOut
import argparse
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from .heuristics import initialize_all_heuristics
from .units import Unit, UnitRegistry, initialize_all_units
from .slots import SlotRegistry, initialize_all_slots
from .tasks import Task, TaskManager

def setup_logging(verbosity: int):
    """Configure logging based on verbosity."""
    log_level = logging.DEBUG if verbosity > 1 else logging.INFO

    # Clear existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Configure root logger
    logging.basicConfig(
        format='%(levelname)s - %(name)s - %(message)s',
        level=log_level,
        force=True
    )

@dataclass
class HeuristicStats:
    """Track statistics for heuristic performance."""
    successes: int = 0
    failures: int = 0
    aborts: int = 0
    total_time: float = 0.0
    last_used: float = 0.0
    
    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

class EnhancedTaskManager(TaskManager):
    """Enhanced task manager with better heuristic integration."""
    
    def __init__(self):
        super().__init__()
        self.heuristic_stats: Dict[str, HeuristicStats] = {}
        self.user_impatience: float = 1.0
        self.map_cycle_time: float = 0.0
        self.credit_assignment_counter: int = 1
        
    def merge_tasks(self, task1: Task, task2: Task) -> Task:
        """Merge two related tasks, combining their reasons and adjusting priority."""
        new_priority = max(task1.priority, task2.priority) + \
                      min(100, 10 * len(set(task1.reasons + task2.reasons)))
        
        return Task(
            priority=min(1000, new_priority),
            unit_name=task1.unit_name,
            slot_name=task1.slot_name,
            reasons=list(set(task1.reasons + task2.reasons)),
            task_type=task1.task_type,
            supplemental=task1.supplemental
        )
    
    def record_heuristic_result(self, heuristic_name: str, success: bool, 
                              execution_time: float, aborted: bool = False):
        """Record the outcome of applying a heuristic."""
        if heuristic_name not in self.heuristic_stats:
            self.heuristic_stats[heuristic_name] = HeuristicStats()
        
        stats = self.heuristic_stats[heuristic_name]
        stats.last_used = self.credit_assignment_counter
        stats.total_time += execution_time
        
        if aborted:
            stats.aborts += 1
        elif success:
            stats.successes += 1
        else:
            stats.failures += 1
            
        self.credit_assignment_counter += 1

    def adjust_unit_worth(self, unit_name: str, delta: int):
        """Adjust the worth of a unit based on task outcomes."""
        unit = self.unit_registry.get_unit(unit_name)
        if unit:
            current_worth = unit.worth_value()
            new_worth = max(0, min(1000, current_worth + delta))
            unit.set_prop('worth', new_worth)

class Eurisko:
    """Enhanced main Eurisko system class."""
    
    def __init__(self, verbosity):
        self.verbosity = verbosity
        UnitRegistry.reset_instance()
        self.unit_registry = UnitRegistry.get_instance()
        self.slot_registry = SlotRegistry()
        self.task_manager = EnhancedTaskManager()
        self.task_manager.verbosity = verbosity
        setup_logging(verbosity)
        self.logger = logging.getLogger(__name__)
        self.units_focused_on = set()
        
    def initialize(self) -> None:
        """Initialize the core concepts and slots."""
        initialize_all_slots(self.slot_registry)
        initialize_all_units(self.unit_registry)
        initialize_all_heuristics(self.unit_registry)
        self._initialize_test_applications(self.unit_registry)
        self._generate_initial_tasks()

    def _initialize_test_applications(self, registry):
        """Initialize some test applications for units."""
        add = registry.get_unit('add')
        if add:
            applications = [
                {'args': [1, 2], 'result': 3, 'worth': 800},
                {'args': [2, 3], 'result': 5, 'worth': 600},
                {'args': [3, 4], 'result': 7, 'worth': 400}
            ]
            add.set_prop('applics', applications)
            add.set_prop('applications', applications)

        multiply = registry.get_unit('multiply')
        if multiply:
            applications = [
                {'args': [2, 3], 'result': 6, 'worth': 900},
                {'args': [3, 4], 'result': 12, 'worth': 500},
                {'args': [4, 5], 'result': 20, 'worth': 300}
            ]
            multiply.set_prop('applics', applications)
            multiply.set_prop('applications', applications)

    def _generate_initial_tasks(self):
        """Generate initial tasks focusing on core operations."""
        # Start with operations that have applications
        for op_name in ['add', 'multiply']:
            op = self.unit_registry.get_unit(op_name)
            if op and op.get_prop('applics'):
                # Add specialization task for ops with mixed success
                task = Task(
                    priority=500,
                    unit_name=op_name,
                    slot_name='specializations',
                    reasons=['Initial specialization exploration'],
                    task_type='specialization',
                    supplemental={'task_type': 'specialization'}
                )
                self.task_manager.add_task(task)

                # Add application finding task
                task = Task(
                    priority=450,
                    unit_name=op_name,
                    slot_name='applics',
                    reasons=['Find additional applications'],
                    task_type='find_applications',
                    supplemental={'task_type': 'find_applications'}
                )
                self.task_manager.add_task(task)

        # Add tasks for other key operations
        for op_name in ['compose', 'set-union', 'list-union', 'bag-union']:
            op = self.unit_registry.get_unit(op_name)
            if op:
                task = Task(
                    priority=400,
                    unit_name=op_name,
                    slot_name='analyze',
                    reasons=[f'Initial analysis of {op_name} operation'],
                    task_type='analysis',
                    supplemental={'task_type': 'analysis'}
                )
                self.task_manager.add_task(task)

    def run(self, eternal_mode: bool = False, 
            max_cycles: Optional[int] = None,
            max_in_cycle: Optional[int] = None) -> None:
        """Run the enhanced main Eurisko loop."""
        self.logger.info("Starting Eurisko")
        self.logger.info(f"Eternal mode: {eternal_mode}")

        cycle_count = 0
        while True:
            cycle_count += 1
            self.task_manager.cycle_stats.clear()
            self.logger.info(f"Starting cycle {cycle_count}")

            if max_cycles and cycle_count > max_cycles:
                self.logger.info(f"Reached maximum cycles ({max_cycles})")
                break

            # Process regular agenda tasks
            tasks_processed = self._process_agenda_tasks(max_in_cycle)
            
            if not tasks_processed and not eternal_mode:
                self.logger.info("Agenda empty, switching to unit exploration")
                # Find unexplored high-worth units
                unexplored_units = [u for u in self.unit_registry.all_units().values()
                                  if u.worth_value() > 800 and 
                                  u.name not in self.units_focused_on]
                
                if not unexplored_units:
                    if eternal_mode:
                        self.logger.info("Resetting explored units list")
                        self.units_focused_on.clear()
                        continue
                    else:
                        self.logger.info("No more high-worth units to explore, ending run")
                        break
                
                # Work on highest worth unexplored unit
                best_unit = max(unexplored_units, key=lambda u: u.worth_value())
                self._work_on_unit(best_unit.name)
                self.units_focused_on.add(best_unit.name)

            # Generate new tasks in eternal mode
            if eternal_mode:
                self.logger.info("Looking for new tasks...")
                self._generate_new_tasks()
                
                if not self.task_manager.has_tasks():
                    self.logger.info("Resetting explored units")
                    self.units_focused_on.clear()

            # Print cycle stats
            self._print_cycle_stats(cycle_count)

    def _process_agenda_tasks(self, max_in_cycle: Optional[int]) -> int:
        """Process tasks from the agenda up to max_in_cycle limit."""
        in_cycle_count = 0
        while self.task_manager.has_tasks():
            in_cycle_count += 1
            if max_in_cycle and in_cycle_count > max_in_cycle:
                self.logger.info(f"Reached maximum count in cycle ({max_in_cycle})")
                break
                
            task = self.task_manager.next_task()
            if task:
                self.logger.info(
                    f"Working on task {task.unit_name}:{task.slot_name} "
                    f"(Priority: {task.priority})"
                )
                result = self._work_on_task(task)
                self.logger.info(f"Task completed with status: {result.get('status')}")
                
                # Adjust unit worth based on task outcome
                if result.get('status') == 'success':
                    self.task_manager.adjust_unit_worth(task.unit_name, 50)
                elif result.get('status') == 'failure':
                    self.task_manager.adjust_unit_worth(task.unit_name, -20)
                    
        return in_cycle_count

    def _work_on_task(self, task: Task) -> Dict[str, Any]:
        """Enhanced task execution with heuristic application and monitoring."""
        from time import time
        
        start_time = time()
        result = {'status': 'failure', 'modifications': []}
        
        # Get applicable heuristics
        applicable_heuristics = self._get_applicable_heuristics(task)
        
        for heuristic in applicable_heuristics:
            h_start = time()
            try:
                success = heuristic.apply(task, self.unit_registry)
                execution_time = time() - h_start
                
                self.task_manager.record_heuristic_result(
                    heuristic.name, success, execution_time
                )
                
                if success:
                    result['status'] = 'success'
                    result['modifications'].append({
                        'heuristic': heuristic.name,
                        'time': execution_time
                    })
                    
            except Exception as e:
                self.logger.error(f"Error applying heuristic {heuristic.name}: {str(e)}")
                self.task_manager.record_heuristic_result(
                    heuristic.name, False, time() - h_start, aborted=True
                )
        
        result['total_time'] = time() - start_time
        return result

    def _work_on_unit(self, unit_name: str) -> None:
        """Direct exploration of a unit using applicable heuristics."""
        unit = self.unit_registry.get_unit(unit_name)
        if not unit:
            return
        
        self.logger.info(f"Focusing on unit: {unit_name}")
        
        # Get heuristics that can work directly on units
        unit_heuristics = self._get_unit_heuristics()
        
        for heuristic in unit_heuristics:
            try:
                heuristic.apply_to_unit(unit, self.unit_registry)
            except Exception as e:
                self.logger.error(f"Error applying heuristic to unit: {str(e)}")

    def _get_applicable_heuristics(self, task: Task) -> List:
        """Get heuristics that could be applied to the task.

        This method filters and ranks available heuristics based on:
        1. Task type compatibility
        2. Historical performance
        3. Heuristic worth values
        4. Success rates
        """
        from typing import List, Tuple
        import operator

        applicable = []
        unit = self.unit_registry.get_unit(task.unit_name)
        if not unit:
            return []

        # Get all available heuristics
        heuristics = self._get_all_heuristics()

        for heuristic in heuristics:
            # Check basic applicability conditions
            if not self._is_heuristic_applicable(heuristic, task, unit):
                continue

            # Calculate a score for this heuristic
            score = self._calculate_heuristic_score(heuristic, task)
            applicable.append((heuristic, score))

        # Sort by score and return just the heuristics
        applicable.sort(key=operator.itemgetter(1), reverse=True)
        return [h for h, _ in applicable]

    def _is_heuristic_applicable(self, heuristic, task: Task, unit: Unit) -> bool:
        """Check if a heuristic is applicable to the given task and unit."""

        # Check if heuristic is enabled
        if not heuristic.is_enabled():
            return False

        # Check task type compatibility
        task_type = task.supplemental.get('task_type')
        if task_type:
            compatible_types = heuristic.get_prop('compatible_task_types', [])
            if compatible_types and task_type not in compatible_types:
                return False

        # Check if heuristic has required conditions
        if_potentially_relevant = heuristic.get_prop('if_potentially_relevant')
        if if_potentially_relevant:
            context = {
                'unit': unit,
                'task': task,
                'system': self.unit_registry,
                'task_manager': self.task_manager
            }
            try:
                if not if_potentially_relevant(heuristic, context):
                    return False
            except Exception as e:
                self.logger.error(f"Error checking potential relevance of {heuristic.name}: {e}")
                return False

        return True

    def _calculate_heuristic_score(self, heuristic, task: Task) -> float:
        """Calculate a score for how applicable/promising a heuristic is for a task."""

        # Get heuristic stats
        stats = self.task_manager.heuristic_stats.get(heuristic.name, HeuristicStats())

        # Base score is the heuristic's worth
        score = heuristic.get_prop('worth', 500) / 1000.0

        # Adjust based on success rate (if we have enough data)
        total_tries = stats.successes + stats.failures
        if total_tries > 0:
            success_rate = stats.successes / total_tries
            score *= (0.5 + success_rate)  # Scale from 0.5x to 1.5x based on success

        # Penalize for high abort rate
        if total_tries > 0:
            abort_rate = stats.aborts / total_tries
            score *= (1.0 - abort_rate * 0.5)  # Up to 50% penalty for aborts

        # Consider average execution time
        if total_tries > 0:
            avg_time = stats.total_time / total_tries
            if avg_time > 1.0:  # If average time > 1 second
                score *= (1.0 / avg_time) ** 0.5  # Gradual penalty for slow heuristics

        # Boost score for task-type specific heuristics
        task_type = task.supplemental.get('task_type')
        if task_type:
            compatible_types = heuristic.get_prop('compatible_task_types', [])
            if task_type in compatible_types:
                score *= 1.2  # 20% boost for task-type specific heuristics

        # Consider recency of last use
        if stats.last_used > 0:
            recency = (self.task_manager.credit_assignment_counter - stats.last_used) / 1000.0
            score *= (1.0 - min(0.5, recency))  # Up to 50% penalty for old heuristics

        return score

    def _get_unit_heuristics(self) -> List:
        """Get heuristics that work directly on units.

        These are heuristics specifically designed for unit exploration
        and manipulation, rather than task-specific operations.
        """
        exploration_heuristics = []

        # Get all available heuristics
        all_heuristics = self._get_all_heuristics()

        for heuristic in all_heuristics:
            # Check if heuristic is enabled
            if not heuristic.is_enabled():
                continue

            # Check if heuristic is designed for unit exploration
            if any([
                heuristic.get_prop('unit_explorer', False),  # Explicit flag
                'explore' in heuristic.get_prop('compatible_task_types', []),
                'analyze' in heuristic.get_prop('compatible_task_types', []),
                heuristic.get_prop('arity', 0) == 1,  # Single unit operations
            ]):
                exploration_heuristics.append(heuristic)

        # Sort by worth
        exploration_heuristics.sort(
            key=lambda h: h.get_prop('worth', 0),
            reverse=True
        )

        return exploration_heuristics

    def _get_all_heuristics(self) -> List:
        """Get all available heuristics from the registry."""
        return [
            unit for unit in self.unit_registry.all_units().values()
            if 'Heuristic' in unit.get_prop('is_a', [])
        ]

    def _generate_new_tasks(self) -> None:
        """Generate new tasks when agenda is empty."""
        # Look for high-worth units that haven't been examined recently
        current_time = self.task_manager.credit_assignment_counter
        
        for unit_name, unit in self.unit_registry.all_units().items():
            if unit.worth_value() > 800:
                # Create examination tasks for high-worth units
                task = Task(
                    unit.worth_value(),
                    unit_name,
                    'examine',
                    ['high worth unit needs examination'],
                    'examination',
                    {'last_examined': current_time}
                )
                self.task_manager.add_task(task)
                
            # Look for potential relationships between units
            self._generate_relationship_tasks(unit)

    def _generate_relationship_tasks(self, unit: Unit) -> None:
        """Generate tasks to explore potential relationships between units."""
        # Implementation would look for patterns and potential connections
        # between units that might be worth exploring
        pass

    def _print_cycle_stats(self, cycle_count: int) -> None:
        """Print detailed statistics for the cycle."""
        self.logger.info(f"Cycle {cycle_count} stats:")
        self.logger.info(f"  Tasks executed: {self.task_manager.cycle_stats['tasks_executed']}")
        self.logger.info(f"  Units created: {self.task_manager.cycle_stats['units_created']}")
        self.logger.info(f"  Units modified: {self.task_manager.cycle_stats['units_modified']}")
        
        # Print heuristic performance stats
        if self.verbosity > 1:
            self.logger.info("Heuristic Performance:")
            for h_name, stats in self.task_manager.heuristic_stats.items():
                self.logger.info(
                    f"  {h_name}: {stats.success_rate:.2%} success rate "
                    f"({stats.successes}/{stats.successes + stats.failures})"
                )

def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser(description='PyEurisko - A Python implementation of Eurisko')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                        help='Verbosity level (0-3)')
    parser.add_argument('-e', '--eternal', action='store_true',
                        help='Run in eternal mode')
    parser.add_argument('-c', '--max-cycles', type=int,
                        help='Maximum number of cycles to run in eternal mode')
    parser.add_argument('-n', '--max-in-cycle', type=int,
                        help='Maximum number of tasks processed in one cycle')
    parser.add_argument('-t', '--timeout', type=int,
                        help='Global run timeout')
    args = parser.parse_args()

    eurisko = Eurisko(verbosity=args.verbosity)
    eurisko.initialize()
    def eurisko_run():
        eurisko.run(eternal_mode=args.eternal, max_cycles=args.max_cycles, max_in_cycle=args.max_in_cycle)
    if args.timeout:
        try:
            func_timeout(args.timeout, eurisko_run)
        except FunctionTimedOut:
            logger.debug("Function timed out")
    else:
        eurisko_run()
    eurisko.task_manager.print_stats()

if __name__ == '__main__':
    main()
