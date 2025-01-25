#!/usr/bin/env python3
"""
Traditional script for running PyEurisko with command line arguments
for better control and monitoring.
"""

import argparse
import logging
import time
from eurisko.main import Eurisko

def setup_logging(verbosity):
    """Configure logging based on verbosity level."""
    log_level = logging.DEBUG if verbosity > 1 else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def print_status(eurisko):
    """Print current system statistics."""
    total_units = len(eurisko.unit_registry.all_units())
    total_slots = len(eurisko.slot_registry.all_slots())
    has_tasks = eurisko.task_manager.has_tasks()
    
    print("\nCurrent Status:")
    print(f"Total units: {total_units}")
    print(f"Total slots: {total_slots}")
    print(f"Has pending tasks: {has_tasks}")

def main():
    parser = argparse.ArgumentParser(description='Run PyEurisko with specified parameters')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                       help='Verbosity level (0-3)')
    parser.add_argument('-c', '--cycles', type=int, default=10,
                       help='Number of cycles to run')
    parser.add_argument('-i', '--interval', type=float, default=2.0,
                       help='Status print interval in seconds')
    args = parser.parse_args()

    logger = setup_logging(args.verbosity)
    logger.info("Initializing PyEurisko...")

    # Initialize the system
    eurisko = Eurisko(verbosity=args.verbosity)
    eurisko.initialize()
    
    try:
        logger.info(f"Running for {args.cycles} cycles...")
        last_status_time = time.time()
        cycle_count = 0
        
        while cycle_count < args.cycles:
            logger.info(f"\nStarting cycle {cycle_count + 1}")
            
            # Process tasks for this cycle
            tasks_processed = False
            while eurisko.task_manager.has_tasks():
                task = eurisko.task_manager.next_task()
                if task:
                    logger.info(f"Processing task: {task.unit_name}")
                    eurisko.task_manager.work_on_task(task)
                    tasks_processed = True
            
            if tasks_processed:
                cycle_count += 1
                
            # Generate new tasks for next cycle
            eurisko._generate_new_tasks()
            
            # Print status at specified intervals
            current_time = time.time()
            if current_time - last_status_time >= args.interval:
                print_status(eurisko)
                last_status_time = current_time
                
            # Small delay to prevent CPU overuse
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt, shutting down...")
    finally:
        print_status(eurisko)
        logger.info("Run completed")

if __name__ == '__main__':
    main()
