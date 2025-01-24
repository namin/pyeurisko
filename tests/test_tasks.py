import pytest
from eurisko.tasks import Task, TaskManager
from eurisko.unit import Unit, UnitRegistry

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

def test_task_manager():
    """Test task manager functionality."""
    manager = TaskManager()
    unit_registry = UnitRegistry()
    
    # Create and register a test unit
    test_unit = Unit("test_unit", worth=500)
    unit_registry.register(test_unit)
    
    # Create some tasks
    task1 = Task(priority=500, unit_name="test_unit", slot_name="slot1", reasons=["r1"])
    task2 = Task(priority=600, unit_name="test_unit", slot_name="slot2", reasons=["r2"])
    
    # Add tasks and verify ordering
    manager.add_task(task1)
    manager.add_task(task2)
    
    assert len(manager.agenda) == 2
    assert manager.next_task().priority == 600  # Higher priority task should be first

def test_task_merging():
    """Test merging of similar tasks."""
    manager = TaskManager()
    
    # Create two tasks for the same unit/slot
    task1 = Task(priority=500, 
                 unit_name="test_unit",
                 slot_name="test_slot",
                 reasons=["reason1"])
    
    task2 = Task(priority=600,
                 unit_name="test_unit",
                 slot_name="test_slot",
                 reasons=["reason2"])
    
    manager.add_task(task1)
    manager.add_task(task2)
    
    # Should merge into one task
    assert len(manager.agenda) == 1
    merged_task = manager.next_task()
    assert len(merged_task.reasons) == 2
    assert merged_task.priority > 600  # Priority should be increased

def test_task_minimum_priority():
    """Test minimum priority filtering."""
    manager = TaskManager()
    manager.min_priority = 500
    
    low_task = Task(priority=400,
                    unit_name="test_unit",
                    slot_name="test_slot",
                    reasons=["r1"])
    
    high_task = Task(priority=600,
                     unit_name="test_unit",
                     slot_name="test_slot",
                     reasons=["r2"])
    
    manager.add_task(low_task)
    manager.add_task(high_task)
    
    # Only high priority task should be added
    assert len(manager.agenda) == 1
    assert manager.next_task().priority == 600
