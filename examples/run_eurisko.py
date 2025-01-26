#!/usr/bin/env python3
"""
Enhanced PyEurisko implementation with closer alignment to original Eurisko behavior.
"""

import argparse
import logging
import time
from typing import Dict, List
from collections import defaultdict
from eurisko.main import Eurisko
from eurisko.unit import Unit
from eurisko.heuristics import Heuristic
from eurisko.concepts import initialize_core_concepts
from eurisko.init_heuristics import initialize_all_heuristics
from eurisko.tasks import Task

class EnhancedEurisko(Eurisko):
    """Enhanced Eurisko implementation with additional features."""
    
    def __init__(self, verbosity: int = 1):
        super().__init__(verbosity=verbosity)
        self.heuristic_stats = defaultdict(lambda: {'tries': 0, 'successes': 0})
        self.synthesized_units = set()
        self.task_results = {}
        
    def get_task_result(self, key: str, default=None):
        """Get a task result by key."""
        return self.task_results.get(key, default)
        
    def add_task_result(self, key: str, value: Any):
        """Add a task result."""
        self.task_results[key] = value

    def initialize(self):
        """Initialize system with core units and concepts."""
        super().initialize()
        initialize_core_concepts(self.unit_registry)
        initialize_all_heuristics(self.unit_registry)
        self._generate_initial_tasks()

    def _generate_initial_tasks(self):
        """Generate initial tasks focusing on core operations."""
        # Start with operations that have applications
        for op_name in ['ADD', 'MULTIPLY']:
            op = self.unit_registry.get_unit(op_name)
            if op and op.get_prop('applics'):
                # Add specialization task for ops with mixed success
                task = Task(
                    priority=500,
                    unit_name=op_name,
                    slot_name='specializations',
                    reasons=['Initial specialization exploration'],
                    supplemental={'task_type': 'specialization'}
                )
                self.task_manager.add_task(task)
                
                # Add application finding task
                task = Task(
                    priority=450,
                    unit_name=op_name,
                    slot_name='applics',
                    reasons=['Find additional applications'],
                    supplemental={'task_type': 'find_applications'}
                )
                self.task_manager.add_task(task)
            
        # Add tasks for other key operations
        for op_name in ['COMPOSE', 'SET-UNION', 'LIST-UNION', 'BAG-UNION']:
            op = self.unit_registry.get_unit(op_name)
            if op:
                task = Task(
                    priority=400,
                    unit_name=op_name,
                    slot_name='analyze',
                    reasons=[f'Initial analysis of {op_name} operation'],
                    supplemental={'task_type': 'analysis'}
                )
                self.task_manager.add_task(task)

    def track_heuristic_result(self, heuristic_name: str, success: bool):
        """Track success/failure statistics for heuristics."""
        stats = self.heuristic_stats[heuristic_name]
        stats['tries'] += 1
        if success:
            stats['successes'] += 1

    def work_on_task(self, task: Task) -> bool:
        """Enhanced task processing with detailed logging and tracking."""
        logger = logging.getLogger(__name__)
        logger.info(f"Focusing on {task.unit_name}")
        
        # Get the unit to work on
        unit = self.unit_registry.get_unit(task.unit_name)
        if not unit:
            logger.warning(f"Unit {task.unit_name} not found")
            return False
            
        # Create comprehensive context for heuristics
        context = {
            'unit': unit,
            'task': task,
            'system': self,
            'registry': self.unit_registry,
            'task_results': {},
            'applics': unit.get_prop('applics') or [],
            'applications': unit.get_prop('applications') or [],
            'worth': unit.get_prop('worth', 500)
        }
        
        # Apply relevant heuristics
        results = []
        for h_name in self.unit_registry.get_units_by_category('heuristic'):
            heuristic = self.unit_registry.get_unit(h_name)
            if not heuristic:
                continue
                
            # Check if heuristic is potentially relevant
            if_relevant = heuristic.get_prop('if_potentially_relevant')
            if if_relevant:
                print(f"\nAttempting to check relevance for {h_name} on {task.unit_name}", flush=True)
                print(f"Applications: {unit.get_prop('applics')}", flush=True)
                try:
                    is_relevant = if_relevant(context)
                    print(f"Got relevance result: {is_relevant}", flush=True)
                except Exception as e:
                    logger.error(f"Error checking relevance for {h_name}: {e}")
                    continue
                    
                if not is_relevant:
                    logger.info(f"        the IF-POTENTIALLY-RELEVANT slot of {h_name} didn't hold for {task.unit_name}")
                    continue
                
            if_truly = heuristic.get_prop('if_truly_relevant')
            if if_truly:
                try:
                    is_truly_relevant = if_truly(context)
                except Exception as e:
                    logger.error(f"Error checking true relevance for {h_name}: {e}")
                    continue
                    
                if not is_truly_relevant:
                    logger.info(f"        the IF-TRULY-RELEVANT slot of {h_name} didn't hold for {task.unit_name}")
                    continue
                
            # Apply heuristic actions
            success = False
            then_compute = heuristic.get_prop('then_compute')
            if then_compute:
                try:
                    success = then_compute(context)
                    if success:
                        logger.info(f"HEURISTIC {h_name} SUCCEEDED")
                    else:
                        logger.info(f"        heuristic {h_name} failed")
                except Exception as e:
                    logger.error(f"Error in compute action for {h_name}: {e}")

            then_add = heuristic.get_prop('then_add_to_agenda')
            if then_add:
                try:
                    success = then_add(context) or success
                    if success:
                        logger.info(f"        heuristic {h_name} agenda success")
                except Exception as e:
                    logger.error(f"Error in add to agenda for {h_name}: {e}")
                    
            # Track results
            self.track_heuristic_result(h_name, success)
            results.append({'heuristic': h_name, 'success': success})
            
            if success:
                logger.info(f"Heuristic {h_name} achieved success!")
                
        return any(r['success'] for r in results)

    def print_detailed_status(self):
        """Print detailed system status including heuristic performance."""
        total_units = len(self.unit_registry.all_units())
        total_slots = len(self.slot_registry.all_slots())
        synthesized = len(self.synthesized_units)
        
        # Count units by category
        categories = defaultdict(int)
        for unit in self.unit_registry.all_units().values():
            for category in unit.isa():
                categories[category] += 1
        
        print(f"\nSystem Status:")
        print(f"Total units: {total_units}, of which {synthesized} were synthesized by Eurisko")
        print("\nUnits by category:")
        print(f" there are {categories['heuristic']} HEURISTICs")
        print(f" there are {categories['MATH-OP']} MATH-OPs")
        print(f" there are {categories['MATH-OBJ']} MATH-OBJs")
        print(f" there are {categories['REPR-CONCEPT']} REPR-CONCEPTs")
        
        # Only show heuristic performance if we have data
        if self.heuristic_stats:
            print("\nHeuristic Performance:")
            for h_name, stats in sorted(self.heuristic_stats.items()):
                success_rate = (stats['successes'] / stats['tries'] * 100) if stats['tries'] > 0 else 0
                print(f"{h_name} -> {success_rate:.0f}% ({stats['tries']} tries, {stats['successes']} successes)")

    def _generate_new_tasks(self):
        """Override to generate tasks based on current system state."""
        # Get units that need analysis
        for unit in self.unit_registry.all_units().values():
            if not unit.get_prop('analyzed') and unit.is_a('MATH-OP'):
                task = Task(
                    priority=400,
                    unit_name=unit.name,
                    slot_name='analyze',
                    reasons=['Operation needs analysis'],
                    supplemental={'task_type': 'analysis'}
                )
                self.task_manager.add_task(task)
        
        super()._generate_new_tasks()

def init_test_applications(registry):
    """Initialize some test applications for units."""
    add = registry.get_unit('ADD')
    if add:
        applications = [
            {'args': [1, 2], 'result': 3, 'worth': 800},
            {'args': [2, 3], 'result': 5, 'worth': 600},
            {'args': [3, 4], 'result': 7, 'worth': 400}
        ]
        add.set_prop('applics', applications)
        add.set_prop('applications', applications)

    multiply = registry.get_unit('MULTIPLY')
    if multiply:
        applications = [
            {'args': [2, 3], 'result': 6, 'worth': 900},
            {'args': [3, 4], 'result': 12, 'worth': 500},
            {'args': [4, 5], 'result': 20, 'worth': 300}
        ]
        multiply.set_prop('applics', applications)
        multiply.set_prop('applications', applications)

def main():
    parser = argparse.ArgumentParser(description='Run Enhanced PyEurisko')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                       help='Verbosity level (0-3)')
    parser.add_argument('-c', '--cycles', type=int, default=10,
                       help='Number of cycles to run')
    parser.add_argument('-i', '--interval', type=float, default=2.0,
                       help='Status print interval in seconds')
    args = parser.parse_args()

    # Configure logging with a simpler format
    logging.basicConfig(
        level=logging.DEBUG if args.verbosity > 1 else logging.INFO,
        format='%(message)s'  # Simplified format without timestamp and level
    )
    logger = logging.getLogger()
    
    # Initialize enhanced system
    eurisko = EnhancedEurisko(verbosity=args.verbosity)
    eurisko.initialize()
    init_test_applications(eurisko.unit_registry)
    
    # Debug: Check applications
    add = eurisko.unit_registry.get_unit('ADD')
    multiply = eurisko.unit_registry.get_unit('MULTIPLY')
    if add:
        print(f"ADD applications: {add.get_prop('applications')}")
    if multiply:
        print(f"MULTIPLY applications: {multiply.get_prop('applications')}")
    
    try:
        logger.info("Eurisko system initialized")
        logger.info(f"Running for {args.cycles} cycles...")
        last_status_time = time.time()
        cycle_count = 0
        
        while cycle_count < args.cycles:
            logger.info(f"\nStarting cycle {cycle_count + 1}")
            
            tasks_processed = False
            while eurisko.task_manager.has_tasks():
                task = eurisko.task_manager.next_task()
                if task:
                    eurisko.work_on_task(task)
                    tasks_processed = True
            
            if tasks_processed:
                cycle_count += 1
            
            # Generate new tasks
            eurisko._generate_new_tasks()
            
            # Print status at intervals
            current_time = time.time()
            if current_time - last_status_time >= args.interval:
                eurisko.print_detailed_status()
                last_status_time = current_time
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt, shutting down...")
    finally:
        eurisko.print_detailed_status()
        logger.info("Run completed")

if __name__ == '__main__':
    main()