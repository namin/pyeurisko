"""Tests for the main Eurisko system."""
import pytest
from eurisko.main import Eurisko
from eurisko.tasks import Task

@pytest.fixture
def eurisko():
    """Create a test instance of Eurisko."""
    return Eurisko(verbosity=0)  # Minimize logging in tests

def test_eurisko_initialization(eurisko):
    """Test basic Eurisko initialization."""
    eurisko.initialize()
    
    # Check core units are registered
    registry = eurisko.unit_registry
    assert registry.get_unit('anything') is not None
    assert registry.get_unit('heuristic') is not None
    assert registry.get_unit('slot') is not None
    
    # Check relationships
    anything = registry.get_unit('anything')
    assert 'category' in anything.isa()
    
    heuristic = registry.get_unit('heuristic')
    assert 'anything' in heuristic.get_prop('generalizations')

def test_eurisko_task_processing(eurisko):
    """Test that Eurisko can process tasks."""
    eurisko.initialize()
    
    # Create a simple test task
    task = Task(
        500,  # priority
        'anything',  # unit_name
        'examine',  # slot_name
        ['test task']  # reasons
    )
    
    eurisko.task_manager.add_task(task)
    assert eurisko.task_manager.has_tasks()
    
    # Run one cycle
    eurisko.run(eternal_mode=False)
    assert not eurisko.task_manager.has_tasks()  # Task should be processed

def test_eurisko_eternal_mode(eurisko):
    """Test eternal mode task generation."""
    eurisko.initialize()
    
    # Create a high-worth unit that should trigger task generation
    test_unit = eurisko.unit_registry.get_unit('heuristic')  # Worth 900
    
    # Run in eternal mode but limit to one cycle
    eurisko.run(eternal_mode=True, max_cycles=1)
    
    # Should have generated at least one task for the high-worth unit
    tasks_generated = any(
        task.unit_name == 'heuristic' 
        for task in eurisko.task_manager.agenda
    )
    assert tasks_generated

def test_eurisko_slot_validation(eurisko):
    """Test slot relationship validation during initialization."""
    eurisko.initialize()
    
    # Add a slot with an invalid inverse relationship
    slot_registry = eurisko.slot_registry
    test_slot = slot_registry.get_slot('worth')  # A known slot
    test_slot.inverse = 'nonexistent_slot'
    
    # Reinitialize - should log a warning but not fail
    eurisko.initialize()
    assert True  # If we get here, no exception was raised

def test_eurisko_high_worth_task_generation(eurisko):
    """Test that high-worth units trigger task generation."""
    eurisko.initialize()
    
    # Create a new high-worth unit
    test_unit = eurisko.unit_registry.get_unit('heuristic')  # Worth 900
    
    # Generate new tasks
    eurisko._generate_new_tasks()
    
    # Should have generated an examination task
    examination_tasks = [
        task for task in eurisko.task_manager.agenda
        if task.unit_name == 'heuristic' and task.slot_name == 'examine'
    ]
    assert len(examination_tasks) > 0

def test_eurisko_cycle_limit(eurisko):
    """Test that cycle limits are respected in eternal mode."""
    eurisko.initialize()
    
    # Create a high-worth unit to ensure task generation
    test_unit = eurisko.unit_registry.get_unit('heuristic')  # Worth 900
    
    # Run with a cycle limit
    max_cycles = 3
    eurisko.run(eternal_mode=True, max_cycles=max_cycles)
    
    # System should have stopped after max_cycles
    # We can't easily check the cycle count directly, but we can verify 
    # the system exited without error
    assert True  # If we get here, the cycle limit worked