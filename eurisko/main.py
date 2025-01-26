"""Main entry point for PyEurisko."""

import argparse
import logging
from typing import Optional
from .units import Unit, UnitRegistry, initialize_all_units
from .slots import SlotRegistry, initialize_all_slots
from .tasks import Task, TaskManager

class Eurisko:
    """Main Eurisko system class."""
    def __init__(self, verbosity):
        self.verbosity = verbosity
        self.unit_registry = UnitRegistry()
        self.slot_registry = SlotRegistry()
        self.task_manager = TaskManager()
        self.task_manager.verbosity = verbosity
        
        log_level = logging.DEBUG if verbosity > 1 else logging.INFO
        logging.basicConfig(
            format='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=log_level,
        )
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> None:
        """Initialize the core concepts and slots."""
        initialize_all_units(self.unit_registry)
        initialize_all_slots(self.slot_registry)

    def run(self, eternal_mode: bool = False, max_cycles: Optional[int] = None) -> None:
        """Run the main Eurisko loop."""
        self.logger.info("Starting Eurisko")
        self.logger.info(f"Eternal mode: {eternal_mode}")
        
        cycle_count = 0
        while True:
            cycle_count += 1
            self.logger.info(f"Starting cycle {cycle_count}")
            
            # Check cycle limit
            if max_cycles and cycle_count > max_cycles:
                self.logger.info(f"Reached maximum cycles ({max_cycles})")
                break
            
            # Process agenda until empty
            while self.task_manager.has_tasks():
                task = self.task_manager.next_task()
                if task:
                    self.logger.info(
                        f"Working on task {task.unit_name}:{task.slot_name} "
                        f"(Priority: {task.priority})")
                    result = self.task_manager.work_on_task(task)
                    self.logger.info(f"Task completed with status: {result.get('status')}")
            
            if not eternal_mode:
                self.logger.info("Agenda empty, ending run")
                break
                
            # In eternal mode, look for new tasks
            self.logger.info("Looking for new tasks...")
            self._generate_new_tasks()
            
            if not self.task_manager.has_tasks():
                self.logger.info("No new tasks found, ending run")
                break

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

def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser(description='PyEurisko - A Python implementation of Eurisko')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                        help='Verbosity level (0-3)')
    parser.add_argument('-e', '--eternal', action='store_true',
                        help='Run in eternal mode')
    parser.add_argument('-c', '--max-cycles', type=int,
                        help='Maximum number of cycles to run in eternal mode')
    args = parser.parse_args()
    
    eurisko = Eurisko(verbosity=args.verbosity)
    eurisko.initialize()
    eurisko.run(eternal_mode=args.eternal, max_cycles=args.max_cycles)

if __name__ == '__main__':
    main()
