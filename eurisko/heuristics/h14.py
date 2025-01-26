"""H14 heuristic implementation: Create type-based prevention rules."""
from typing import Any, Dict, List, Optional
import logging
import inspect
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h14(heuristic) -> None:
    """Configure H14: Create type-based prevention rules.
    
    This heuristic examines failing concepts to understand type changes that
    led to failure. It creates prevention rules that block problematic type
    transitions (e.g., simple to complex) while still allowing safe changes.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF C is about to die, THEN try to form prevention rules based on "
        "problematic type transformations that led to failure.")
    heuristic.set_prop('abbrev', "Form type-based prevention rules")

    def get_type_category(value: Any) -> str:
        """Determine high-level type category."""
        if callable(value):
            return 'function'
        elif isinstance(value, (list, tuple, set)):
            return 'sequence'
        elif isinstance(value, dict):
            return 'mapping'
        elif isinstance(value, (int, float)):
            return 'numeric'
        elif isinstance(value, str):
            return 'text'
        else:
            return type(value).__name__

    def measure_complexity(value: Any) -> int:
        """Estimate structural complexity of a value."""
        if callable(value):
            try:
                source = inspect.getsource(value)
                return len(source.split('\n'))
            except:
                return 5  # Default for functions
        elif isinstance(value, (list, tuple, set)):
            return sum(measure_complexity(x) for x in value) + 1
        elif isinstance(value, dict):
            return sum(
                measure_complexity(k) + measure_complexity(v)
                for k, v in value.items()
            ) + 1
        elif isinstance(value, str):
            return len(value)
        else:
            return 1

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check if unit is being deleted."""
        unit = context.get('unit')
        deleted_units = context.get('deleted_units', [])
        
        if not unit or unit.name not in deleted_units:
            return False
            
        # Need to know what created this unit
        creditors = unit.get_prop('creditors', [])
        if not creditors:
            return False
            
        # Store creator info for later
        creator = creditors[0]
        context['creator'] = creator
        return True

    @rule_factory
    def then_compute(rule, context):
        """Create type-based prevention rules."""
        unit = context.get('unit')
        creator = context.get('creator')
        if not unit or not creator:
            return False

        # Find creation task and analyze type changes
        unit_apps = unit.get_prop('applications') or []
        creator_unit = unit.get_prop('creditors_applications') or []
        all_apps = unit_apps + creator_unit
        
        creation_task = None
        for app in all_apps:
            task_info = app.get('task_info', {})
            old_value = task_info.get('old_value')
            new_value = task_info.get('new_value')
            
            if old_value is not None and new_value is not None:
                # Analyze type changes
                old_type = type(old_value).__name__
                new_type = type(new_value).__name__
                old_category = get_type_category(old_value)
                new_category = get_type_category(new_value)
                
                old_complexity = measure_complexity(old_value)
                new_complexity = measure_complexity(new_value)
                
                type_analysis = {
                    'from_type': old_type,
                    'to_type': new_type,
                    'from_category': old_category,
                    'to_category': new_category,
                    'type_changed': old_type != new_type,
                    'category_changed': old_category != new_category,
                    'complexity_increased': new_complexity > old_complexity,
                    'complexity_ratio': new_complexity / old_complexity if old_complexity > 0 else float('inf')
                }
                
                if type_analysis['type_changed'] or type_analysis['complexity_increased']:
                    task_info['type_analysis'] = type_analysis
                    creation_task = app
                    break

        if not creation_task:
            return False

        task_info = creation_task.get('task_info', {})
        changed_slot = task_info.get('slot_to_change')
        type_analysis = task_info.get('type_analysis')
        
        if not all([changed_slot, type_analysis]):
            return False

        # Create and register prevention rules
        new_rules = []
        
        # Rule for type changes if relevant
        if type_analysis['type_changed']:
            type_rule_name = (
                f"prevent_{type_analysis['from_type']}_to_"
                f"{type_analysis['to_type']}_changes"
            )
            type_rule = rule.unit_registry.create_unit(type_rule_name)
            if type_rule:
                type_rule.set_prop('type', 'type-prevention-rule')
                type_rule.set_prop('english',
                    f"Prevent changes in {changed_slot} slot that convert "
                    f"{type_analysis['from_type']} values to "
                    f"{type_analysis['to_type']} values")
                type_rule.set_prop('slot_to_avoid', changed_slot)
                type_rule.set_prop('from_type', type_analysis['from_type'])
                type_rule.set_prop('to_type', type_analysis['to_type'])
                type_rule.set_prop('learned_from', unit.name)
                type_rule.set_prop('source_creditor', creator)
                rule.unit_registry.register(type_rule)
                new_rules.append(type_rule)

        # Rule for complexity increases if relevant
        if type_analysis['complexity_increased']:
            complexity_rule_name = f"prevent_complexity_increase_in_{changed_slot}"
            complexity_rule = rule.unit_registry.create_unit(complexity_rule_name)
            if complexity_rule:
                complexity_rule.set_prop('type', 'complexity-prevention-rule')
                complexity_rule.set_prop('english',
                    f"Prevent changes to {changed_slot} slot that significantly "
                    f"increase structural complexity")
                complexity_rule.set_prop('slot_to_avoid', changed_slot)
                complexity_rule.set_prop('check', 'complexity_increase')
                complexity_rule.set_prop('learned_from', unit.name)
                complexity_rule.set_prop('source_creditor', creator)
                complexity_rule.set_prop('complexity_threshold', 
                    type_analysis['complexity_ratio'])
                rule.unit_registry.register(complexity_rule)
                new_rules.append(complexity_rule)

        if new_rules:
            context['task_results'] = context.get('task_results', {})
            context['task_results'].update({
                'new_units': new_rules,
                'type_analysis': type_analysis
            })
            return True

        return False

    @rule_factory
    def then_print_to_user(rule, context):
        """Report on prevention rules created."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        
        if not unit or not task_results:
            return False
            
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False

        type_analysis = task_results.get('type_analysis', {})
        
        logger.info(
            f"\nCreated prevention rules from {unit.name} failure:")
            
        for rule_unit in new_units:
            if rule_unit.get_prop('type') == 'type-prevention-rule':
                logger.info(
                    f"- Type rule: prevent {rule_unit.get_prop('from_type')} to "
                    f"{rule_unit.get_prop('to_type')} conversions in "
                    f"{rule_unit.get_prop('slot_to_avoid')}"
                )
            else:
                logger.info(
                    f"- Complexity rule: prevent large increases "
                    f"(>{type_analysis['complexity_ratio']:.1f}x) in "
                    f"{rule_unit.get_prop('slot_to_avoid')}"
                )
        return True