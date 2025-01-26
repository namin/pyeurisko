"""H18 heuristic implementation: Generalize slot values."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h18(heuristic) -> None:
    """Configure H18: Generalize values in a chosen slot."""
    heuristic.set_prop('worth', 704)
    heuristic.set_prop('english', 
        "IF the current task is to generalize a unit, and a slot has been chosen to "
        "be the one changed, THEN randomly select a part of it and generalize that part")
    heuristic.set_prop('abbrev', "Generalize a given slot of a given unit")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_define_new_concepts', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)
    heuristic.set_prop('then_compute_failed_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we have a slot to generalize."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            return False
            
        slot_to_change = task.get('supplemental', {}).get('slot_to_change')
        if not slot_to_change or task.get('slot') != 'generalizations':
            return False
            
        context['slot_to_change'] = slot_to_change
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print generalization results."""
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        old_value = context.get('old_value')
        new_value = context.get('new_value')
        if not all([unit, slot, old_value is not None, new_value is not None]):
            return False
            
        logger.info(f"\nGeneralized the {slot} slot of {unit.name}, replacing "
                   f"its old value ({old_value}) by {new_value}.")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Perform slot generalization."""
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        if not all([unit, slot]):
            return False
            
        # Track values and dependencies
        context['unit_diff'] = []
        context['are_units'] = []
        context['have_genl'] = []
        
        # Get current value
        old_value = unit.get_prop(slot)
        if old_value is None:
            return False
            
        # Get data type and generalize based on type
        data_type = unit.get_prop('data_type', 'default')
        try:
            if data_type == 'list':
                if isinstance(old_value, list) and len(old_value) > 1:
                    new_value = old_value[:-1]  # Remove last constraint
            elif data_type == 'predicate':
                if callable(old_value):
                    # Make predicate more general by relaxing conditions
                    def generalized_pred(*args):
                        return old_value(*args) or True
                    new_value = generalized_pred
            elif data_type == 'function':
                if callable(old_value):
                    def generalized_func(*args):
                        result = old_value(*args)
                        # Make function more general by extending domain
                        return result if result is not None else args[0]
                    new_value = generalized_func
            else:
                # Default generalization: try making value more abstract
                new_value = rule.unit_registry.get_generalization(old_value)
                
        except Exception as e:
            logger.warning(f"Failed to generalize {slot} of {unit.name}: {e}")
            new_value = old_value
            
        if new_value == old_value:
            logger.info(f"\nCouldn't find meaningful generalization of the {slot} "
                       f"slot of {unit.name}")
            return False
            
        context['old_value'] = old_value
        context['new_value'] = new_value
        
        # Create unit to track need for generalization
        need_genl = list(set(context['are_units']) - set(context['have_genl']))
        
        # Update tasks for needed generalizations
        if need_genl:
            for unit_name in need_genl:
                unit = rule.unit_registry.get_unit(unit_name)
                if not unit:
                    continue
                    
                task = {
                    'priority': rule.task_manager.current_priority // 2,
                    'unit': unit_name,
                    'slot': 'generalizations',
                    'reasons': [
                        f"{context['unit'].name} might have been generalized better "
                        f"if some generalizations had existed for {unit_name}"
                    ],
                    'supplemental': {'credit_to': ['h18']}
                }
                rule.task_manager.add_task(task)
                
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_tasks'] = [
                f"{len(need_genl)} units will be generalized because if such "
                f"generalizations had existed, we could have used them just now "
                f"while trying to generalize {unit.name}"
            ]
            context['task_results'] = task_results
            
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Create generalized unit."""
        unit = context.get('unit')
        slot = context.get('slot_to_change')
        new_value = context.get('new_value')
        if not all([unit, slot, new_value]):
            return False
            
        # Create new generalized unit
        new_unit = rule.unit_registry.create_unit(f"{unit.name}-genl")
        if not new_unit:
            return False
            
        # Copy non-sibling slots
        sibling_slots = unit.get_prop('slot_siblings', [])
        for old_slot in unit.get_prop('slots', []):
            if old_slot not in sibling_slots:
                new_unit.set_prop(old_slot, unit.get_prop(old_slot))
                
        # Set generalized value
        new_unit.set_prop(slot, new_value)
        
        # Update unit relationships
        unit.add_to_prop('generalizations', new_unit.name)
        new_unit.add_to_prop('specializations', unit.name)
        
        # Add creditors
        creditors = ['h18']
        if task := context.get('task'):
            task_creditors = task.get('supplemental', {}).get('credit_to', [])
            creditors.extend(task_creditors)
        new_unit.set_prop('creditors', creditors)
        
        # Update task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(new_unit)
        task_results['new_units'] = new_units
        context['task_results'] = task_results
        
        return True