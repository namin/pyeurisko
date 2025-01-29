"""Main entry point for PyEurisko."""

from func_timeout import func_timeout, FunctionTimedOut
import argparse
import logging
from typing import Optional
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

class Eurisko:
    """Main Eurisko system class."""
    def __init__(self, verbosity):
        self.verbosity = verbosity
        UnitRegistry.reset_instance()
        self.unit_registry = UnitRegistry.get_instance()
        self.slot_registry = SlotRegistry()
        self.task_manager = TaskManager()
        self.task_manager.verbosity = verbosity
        setup_logging(verbosity)
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> None:
        """Initialize the core concepts and slots."""
        initialize_all_slots(self.slot_registry)
        initialize_all_units(self.unit_registry)
        initialize_all_heuristics(self.unit_registry)
        self.initialize_test_applications(self.unit_registry)
        self._generate_initial_tasks()

    def run(self, eternal_mode: bool = False, max_cycles: Optional[int] = None, max_in_cycle: Optional[int] = None) -> None:
        """Run the main Eurisko loop."""
        self.logger.info("Starting Eurisko")
        self.logger.info(f"Eternal mode: {eternal_mode}")

        cycle_count = 0
        while True:
            cycle_count += 1
            self.task_manager.cycle_stats.clear()  # Reset cycle stats
            self.logger.info(f"Starting cycle {cycle_count}")

            # Check cycle limit
            if max_cycles and cycle_count > max_cycles:
                self.logger.info(f"Reached maximum cycles ({max_cycles})")
                break

            # Process agenda until empty
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
                        f"(Priority: {task.priority})")
                    result = self.task_manager.work_on_task(task)
                    self.logger.info(f"Task completed with status: {result.get('status')}")
                
            # Print cycle stats
            self.logger.info(f"Cycle {cycle_count} stats:")
            self.logger.info(f"  Tasks executed: {self.task_manager.cycle_stats['tasks_executed']}")
            self.logger.info(f"  Units created: {self.task_manager.cycle_stats['units_created']}")
            self.logger.info(f"  Units modified: {self.task_manager.cycle_stats['units_modified']}")


            if not eternal_mode:
                self.logger.info("Agenda empty, ending run")
                break

            # In eternal mode, look for new tasks
            self.logger.info("Looking for new tasks...")
            self._generate_new_tasks()

            if not self.task_manager.has_tasks():
                self.logger.info("No new tasks found, ending run")
                break

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

    def _generate_new_tasks(self) -> None:
        """Generate new tasks when agenda is empty."""
        # Look for high-worth units that haven't been examined recently
        for unit_name, unit in self.unit_registry.all_units().items():
            if unit.worth_value() > 800:  # High worth threshold
                task = Task(
                    unit.worth_value(),  # priority
                    unit_name,           # unit_name
                    'examine',           # slot_name
                    ['high worth unit needs examination']  # reasons
                )
                self.task_manager.add_task(task)

    def initialize_test_applications(self, registry):
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
        except FunctionTimeOut:
            logger.debug("Function timed out")
    else:
        eurisko_run()
    eurisko.task_manager.print_stats()

if __name__ == '__main__':
    main()
