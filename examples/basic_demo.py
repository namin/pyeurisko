"""Basic demo of PyEurisko functionality."""
import logging
from eurisko.main import Eurisko
from eurisko.tasks import Task

def main():
    """Run a basic demonstration of Eurisko."""
    # Initialize Eurisko with verbose logging
    eurisko = Eurisko(verbosity=2)
    eurisko.initialize()
    
    # Create a new mathematical concept
    fibonacci = eurisko.unit_registry.get_unit('math-concept')
    fibonacci.name = 'fibonacci'
    fibonacci.set_prop('isa', ['math-concept', 'operation'])
    fibonacci.set_prop('worth', 600)
    fibonacci.set_prop('fast_alg', lambda n: n if n <= 1 else fibonacci.get_prop('fast_alg')(n-1) + fibonacci.get_prop('fast_alg')(n-2))
    
    # Register it
    eurisko.unit_registry.register(fibonacci)
    
    # Create a task to examine it
    task = Task(
        750,  # priority
        'fibonacci',  # unit_name
        'examine',  # slot_name
        ['new mathematical concept needs analysis']  # reasons
    )
    
    eurisko.task_manager.add_task(task)
    
    # Run Eurisko for one cycle
    eurisko.run(eternal_mode=False)
    
    # Print the system state
    print("\nFinal system state:")
    print(f"Number of registered units: {len(eurisko.unit_registry.all_units())}")
    print(f"Number of registered slots: {len(eurisko.slot_registry.all_slots())}")
    print(f"Tasks processed: {eurisko.task_manager.task_num}")

if __name__ == '__main__':
    main()