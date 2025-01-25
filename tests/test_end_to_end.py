"""End-to-end test demonstrating core PyEurisko functionality."""
import pytest
from eurisko.main import Eurisko
from eurisko.tasks import Task
from eurisko.heuristics.base import Heuristic
from eurisko.unit import Unit

def test_end_to_end():
    """Complete end-to-end test of PyEurisko functionality."""
    # Initialize system
    eurisko = Eurisko(verbosity=0)
    eurisko.initialize()
    
    # 1. Create and register a custom heuristic
    class ExampleHeuristic(Heuristic):
        def is_relevant(self, context):
            return 'value' in context and context['value'] > 100
            
        def apply(self, context):
            return context['value'] * 2
    
    h_example = ExampleHeuristic("H-Example", "Example heuristic for testing")
    h_example.set_prop('worth', 500)
    eurisko.unit_registry.register(h_example)
    
    # 2. Create a mathematical concept with properties
    fibonacci = Unit("fibonacci")
    fibonacci.set_prop('isa', ['math-concept', 'operation'])
    fibonacci.set_prop('worth', 600)
    fibonacci.set_prop('value', 150)  # Will trigger our heuristic
    fibonacci.set_prop('fast_alg', 
        lambda n: n if n <= 1 else fibonacci.get_prop('fast_alg')(n-1) + fibonacci.get_prop('fast_alg')(n-2))
    eurisko.unit_registry.register(fibonacci)
    
    # 3. Create tasks to examine unit
    examine_task = Task(
        750,  # priority
        'fibonacci',  # unit_name
        'examine',  # slot_name
        ['new mathematical concept needs analysis']  # reasons
    )
    
    apply_heuristic_task = Task(
        800,  # priority
        'fibonacci',  # unit_name
        'apply_heuristic',  # slot_name
        ['test heuristic application']  # reasons
    )
    
    # 4. Add tasks and run system
    eurisko.task_manager.add_task(examine_task)
    eurisko.task_manager.add_task(apply_heuristic_task)
    
    initial_units = len(eurisko.unit_registry.all_units())
    eurisko.run(eternal_mode=False)
    final_units = len(eurisko.unit_registry.all_units())
    
    # 5. Verify system behavior
    assert final_units >= initial_units, "System should maintain or create units"
    assert eurisko.task_manager.task_num > 0, "Tasks should have been processed"
    
    # Test fibonacci calculation
    fib_unit = eurisko.unit_registry.get_unit('fibonacci')
    assert fib_unit.get_prop('fast_alg')(5) == 5, "Fibonacci calculation should work"
    
    # Test heuristic application
    assert fib_unit.get_prop('value') == 150, "Original value should be preserved"
    
    # Verify system state
    assert len(eurisko.slot_registry.all_slots()) > 0, "Slots should be registered"
    assert eurisko.task_manager.task_num >= 2, "At least initial tasks should be processed"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])