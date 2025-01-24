import pytest
from eurisko.tasks import Task, TaskManager
from eurisko.unit import Unit, UnitRegistry

@pytest.fixture
def task_manager():
    """Create a task manager with a test unit for testing."""
    manager = TaskManager()
    registry = UnitRegistry()
    
    # Create and register a test unit
    test_unit = Unit("test_unit", worth=500)
    registry.register(test_unit)
    
    return manager

@pytest.fixture
def test_unit():
    """Create a test unit with some heuristics."""
    unit = Unit("test_unit", worth=500)
    
    # Add some test heuristics
    unit.set_prop("if_parts", [
        lambda ctx: ctx['value'] > 0,  # Simple test condition
    ])
    
    unit.set_prop("then_parts", [
        lambda ctx: ctx['value'] * 2,  # Simple transformation
    ])
    
    return unit

def test_task_creation():
    """Test basic task creation."""
    task = Task(priority=500,
                unit_name="test_unit",
                slot_name="test_slot",
                reasons=["reason1", "reason2"])
    
    assert task.priority == 500
    assert task.unit_name == "test_unit"
    assert task.slot_name == "test_slot"
    assert len(task.reasons) == 2

def test_task_comparison():
    """Test task priority comparison."""
    task1 = Task(priority=500, unit_name="u1", slot_name="s1", reasons=[])
    task2 = Task(priority=600, unit_name="u2", slot_name="s2", reasons=[])
    task3 = Task(priority=400, unit_name="u3", slot_name="s3", reasons=[])
    
    # Higher priority tasks should come first
    assert task2 < task1  # Reversed because we want higher priority first
    assert task1 < task3

def test_task_manager_basic(task_manager):
    """Test basic task manager functionality."""
    # Create some tasks
    task1 = Task(priority=500, unit_name="test_unit", slot_name="slot1", reasons=["r1"])
    task2 = Task(priority=600, unit_name="test_unit", slot_name="slot2", reasons=["r2"])
    
    # Add tasks and verify ordering
    task_manager.add_task(task1)
    task_manager.add_task(task2)
    
    assert len(task_manager.agenda) == 2
    assert task_manager.next_task().priority == 600  # Higher priority task should be first

def test_task_merging(task_manager):
    """Test merging of similar tasks."""
    # Create two tasks for the same unit/slot
    task1 = Task(priority=500, 
                 unit_name="test_unit",
                 slot_name="test_slot",
                 reasons=["reason1"])
    
    task2 = Task(priority=600,
                 unit_name="test_unit",
                 slot_name="test_slot",
                 reasons=["reason2"])
    
    task_manager.add_task(task1)
    task_manager.add_task(task2)
    
    # Should merge into one task
    assert len(task_manager.agenda) == 1
    merged_task = task_manager.next_task()
    assert len(merged_task.reasons) == 2
    assert merged_task.priority > 600  # Priority should be increased

def test_task_minimum_priority(task_manager):
    """Test minimum priority filtering."""
    task_manager.min_priority = 500
    
    low_task = Task(priority=400,
                    unit_name="test_unit",
                    slot_name="test_slot",
                    reasons=["r1"])
    
    high_task = Task(priority=600,
                     unit_name="test_unit",
                     slot_name="test_slot",
                     reasons=["r2"])
    
    task_manager.add_task(low_task)
    task_manager.add_task(high_task)
    
    # Only high priority task should be added
    assert len(task_manager.agenda) == 1
    assert task_manager.next_task().priority == 600

def test_task_execution_phases(task_manager, test_unit):
    """Test the different phases of task execution."""
    registry = UnitRegistry()
    registry.register(test_unit)
    
    # Add phase-specific heuristics
    test_unit.set_prop("if_about_to_work_on_task", [
        lambda ctx: True  # Always allow task to proceed
    ])
    
    test_unit.set_prop("if_finished_working_on_task", [
        lambda ctx: True  # Always consider task successful
    ])
    
    task = Task(priority=500,
                unit_name="test_unit",
                slot_name="test_slot",
                reasons=["test"])
    
    # Define a simple interpreter
    def test_interpreter(unit, context):
        context['value'] = 42  # Set a test value
        return True
    
    result = task_manager.work_on_task(task, test_interpreter)
    assert result['status'] == 'completed'

def test_task_abort(task_manager, test_unit):
    """Test task abortion functionality."""
    registry = UnitRegistry()
    registry.register(test_unit)
    
    # Add a heuristic that triggers abort
    test_unit.set_prop("if_about_to_work_on_task", [
        lambda ctx: False  # Fail immediately
    ])
    
    task = Task(priority=500,
                unit_name="test_unit",
                slot_name="test_slot",
                reasons=["test"])
    
    result = task_manager.work_on_task(task)
    assert result['status'] == 'aborted'
    assert result['phase'] == 'pre-task'

def test_process_agenda(task_manager):
    """Test processing the entire agenda."""
    # Add multiple tasks
    tasks = [
        Task(priority=500, unit_name="test_unit", slot_name="slot1", reasons=["r1"]),
        Task(priority=600, unit_name="test_unit", slot_name="slot2", reasons=["r2"]),
        Task(priority=400, unit_name="test_unit", slot_name="slot3", reasons=["r3"])
    ]
    
    for task in tasks:
        task_manager.add_task(task)
    
    def simple_interpreter(unit, context):
        return True
    
    results = task_manager.process_agenda(simple_interpreter)
    assert len(results) == 3  # All tasks should be processed
    assert all(r['status'] == 'completed' for r in results)  # All should complete
