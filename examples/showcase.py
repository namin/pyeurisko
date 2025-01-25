"""PyEurisko showcase demonstrating key system capabilities.

This script provides a comprehensive demonstration of PyEurisko's core features:
- Unit creation and registration
- Mathematical concept definition
- Task scheduling and processing
- Heuristic application
- System state monitoring
"""
import logging
from eurisko.main import Eurisko
from eurisko.tasks import Task
from eurisko.heuristics.base import Heuristic

def run_showcase():
    """Run a comprehensive showcase of PyEurisko's features."""
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('PyEurisko-Showcase')
    
    # Initialize system
    logger.info("Initializing PyEurisko system...")
    eurisko = Eurisko(verbosity=1)
    eurisko.initialize()
    
    # Define mathematical functions
    def fib(n):
        """Calculate the nth Fibonacci number iteratively."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def fact(n):
        """Calculate factorial iteratively."""
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result

    logger.info("\nCreating mathematical concepts...")
    
    # Create custom heuristic for analysis
    class MathAnalysisHeuristic(Heuristic):
        def is_relevant(self, context):
            unit = context.get('unit')
            return unit and 'math-concept' in unit.get_prop('isa', [])
            
        def apply(self, context):
            unit = context.get('unit')
            if unit:
                logger.info(f"Analyzing mathematical unit: {unit.name}")
                logger.info(f"- Type: {unit.get_prop('isa')}")
                logger.info(f"- Worth: {unit.get_prop('worth')}")
                return True
            return False
    
    math_analysis = MathAnalysisHeuristic("H-MathAnalysis", "Mathematical concept analyzer")
    math_analysis.set_prop('worth', 500)
    eurisko.unit_registry.register(math_analysis)
    
    # Fibonacci sequence
    fibonacci = eurisko.unit_registry.get_unit('math-concept')
    fibonacci.name = 'fibonacci'
    fibonacci.set_prop('isa', ['math-concept', 'operation'])
    fibonacci.set_prop('worth', 600)
    fibonacci.set_prop('fast_alg', fib)
    eurisko.unit_registry.register(fibonacci)
    logger.info(f"Created Fibonacci concept with worth {fibonacci.get_prop('worth')}")
    
    # Factorial operation
    factorial = eurisko.unit_registry.get_unit('math-concept')
    factorial.name = 'factorial'
    factorial.set_prop('isa', ['math-concept', 'operation'])
    factorial.set_prop('worth', 550)
    factorial.set_prop('fast_alg', fact)
    eurisko.unit_registry.register(factorial)
    logger.info(f"Created Factorial concept with worth {factorial.get_prop('worth')}")
    
    # Create tasks
    logger.info("\nCreating tasks...")
    tasks = [
        Task(800, 'fibonacci', 'analyze', 
             ['mathematical analysis needed']),
        Task(750, 'factorial', 'analyze',
             ['mathematical analysis needed'])
    ]
    
    for task in tasks:
        eurisko.task_manager.add_task(task)
        logger.info(f"Added task for {task.unit_name} with priority {task.priority}")
    
    # Run system
    logger.info("\nRunning PyEurisko...")
    initial_units = len(eurisko.unit_registry.all_units())
    eurisko.run(eternal_mode=False)
    final_units = len(eurisko.unit_registry.all_units())
    
    # Report results
    logger.info("\nExecution complete. System state:")
    logger.info(f"- Initial units: {initial_units}")
    logger.info(f"- Final units: {final_units}")
    logger.info(f"- Registered slots: {len(eurisko.slot_registry.all_slots())}")
    logger.info(f"- Tasks processed: {eurisko.task_manager.task_num}")
    
    # Calculate and display results for multiple inputs
    test_values = [0, 1, 5, 7]
    logger.info("\nMathematical results:")
    
    logger.info("\nFibonacci sequence:")
    for n in test_values:
        result = fib(n)
        logger.info(f"  F({n}) = {result}")
    
    logger.info("\nFactorial sequence:")
    for n in test_values:
        result = fact(n)
        logger.info(f"  {n}! = {result}")
    
    # Display final unit properties
    logger.info("\nMathematical unit properties:")
    for unit_name in ['fibonacci', 'factorial']:
        unit = eurisko.unit_registry.get_unit(unit_name)
        logger.info(f"\n{unit_name.capitalize()} unit:")
        for prop in ['isa', 'worth']:
            logger.info(f"  {prop}: {unit.get_prop(prop)}")

if __name__ == '__main__':
    run_showcase()