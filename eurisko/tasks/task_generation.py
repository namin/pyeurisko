"""Task generation for PyEurisko."""

from typing import List
from .task import Task
from ..units import Unit, UnitRegistry

def get_highest_worth_units(registry: UnitRegistry, n: int = 5) -> List[Unit]:
    """Get the n highest worth units."""
    units = list(registry.all_units().values())
    return sorted(units, key=lambda u: u.worth_value(), reverse=True)[:n]

def generate_initial_tasks(task_manager, unit_registry: UnitRegistry) -> None:
    """Generate initial tasks combining explicit seeding with organic exploration.
    
    This follows a hybrid approach:
    1. Seed with known successful tasks for core operations
    2. Add organic exploration based on unit worth
    """
    # First add core tasks we know can succeed
    core_ops = ['add', 'multiply']
    for op_name in core_ops:
        op = unit_registry.get_unit(op_name)
        if op and op.get_prop('applics'):
            task = Task(
                priority=500,
                unit_name=op_name,
                slot_name='specializations',
                reasons=['Initial specialization exploration'],
                task_type='specialization'
            )
            task_manager.add_task(task)

            task = Task(
                priority=450,
                unit_name=op_name,
                slot_name='applics',
                reasons=['Find additional applications'],
                task_type='find_applications'
            )
            task_manager.add_task(task)

    # Then add organic exploration of high worth units
    high_worth_units = get_highest_worth_units(unit_registry, n=3)
    for unit in high_worth_units:
        # Look for potential specializations
        if unit.get_prop('isa'):
            task = Task(
                priority=unit.worth_value(),
                unit_name=unit.name,
                slot_name='specializations',
                reasons=[f'High worth unit {unit.name} may have useful specializations'],
                task_type='analysis'
            )
            task_manager.add_task(task)

        # Look for generalizations if they exist
        if unit.get_prop('generalizations'):
            task = Task(
                priority=unit.worth_value() - 50,
                unit_name=unit.name,
                slot_name='analyze',
                reasons=[f'Understanding generalizations of {unit.name}'],
                task_type='analysis'
            )
            task_manager.add_task(task)

def generate_ongoing_tasks(task_manager, unit_registry: UnitRegistry) -> None:
    """Generate ongoing tasks balancing exploration with focused investigation."""
    
    # Look at high worth units first
    high_worth_units = get_highest_worth_units(unit_registry, n=5)
    
    tasks_added = 0
    for unit in high_worth_units:
        if tasks_added >= 10:  # Limit number of tasks generated
            break
            
        worth = unit.worth_value()
        if worth > 700:  # High worth threshold
            # Check for unexplored aspects
            if not unit.get_prop('applics'):
                task = Task(
                    priority=worth - 50,
                    unit_name=unit.name,
                    slot_name='applics',
                    reasons=['High worth unit lacks applications'],
                    task_type='analysis'
                )
                task_manager.add_task(task)
                tasks_added += 1
                
            if not unit.get_prop('specializations'):
                task = Task(
                    priority=worth - 25,
                    unit_name=unit.name,
                    slot_name='specializations',
                    reasons=['High worth unit lacks specializations'],
                    task_type='analysis'
                )
                task_manager.add_task(task)
                tasks_added += 1

            # Look for analogies if we have enough worth
            if worth > 800:
                task = Task(
                    priority=worth - 100,
                    unit_name=unit.name,
                    slot_name='analogies',
                    reasons=['Seeking analogies for high worth unit'],
                    task_type='analysis'
                )
                task_manager.add_task(task)
                tasks_added += 1

            # Try synthesis between high worth units
            for other_unit in high_worth_units:
                if other_unit.name != unit.name and other_unit.worth_value() > 700:
                    task = Task(
                        priority=min(worth, other_unit.worth_value()) - 75,
                        unit_name=unit.name,
                        slot_name='synthesize',
                        reasons=[f'Synthesizing with other high worth unit {other_unit.name}'],
                        task_type='synthesis',
                        supplemental={'with_unit': other_unit.name}
                    )
                    task_manager.add_task(task)
                    tasks_added += 1
