"""H20 heuristic implementation: Test on sibling operation inputs."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h20(heuristic) -> None:
    """Configure H20: Run algorithm on sibling operation inputs."""
    heuristic.set_prop('worth', 600)
    heuristic.set_prop('english', "IF an op f can apply to any of the domain items of another op, THEN so apply it and maybe some patterns will emerge")
    heuristic.set_prop('abbrev', "Run f on args used for other ops")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_add_to_agenda', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)
    heuristic.set_prop('then_compute_failed_record', record_func)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check if unit has an algorithm."""
        unit = context.get('unit')
        if not unit:
            return False
        return bool(unit.get_prop('algorithm'))

    @rule_factory
    def if_truly_relevant(rule, context):
        """Check if we have similar ops to test."""
        unit = context.get('unit')
        if not unit or unit.get_prop('subsumed_by'):
            return False
            
        # Find similar operations
        siblings = unit.get_prop('siblings', [])
        space_to_use = []
        unit_arity = unit.get_prop('arity')
        
        for sibling in siblings:
            if sibling == unit.name:
                continue
            sib_unit = rule.unit_registry.get_unit(sibling)
            if not sib_unit:
                continue
            if (sib_unit.get_prop('arity') == unit_arity and 
                len(sib_unit.get_prop('applications', [])) > 3):
                space_to_use.append(sib_unit)
                
        context['space_to_use'] = space_to_use
        context['domain_tests'] = unit.get_prop('domain_tests', [])
        return bool(space_to_use)

    @rule_factory 
    def then_compute(rule, context):
        """Apply algorithm to sibling operation arguments."""
        unit = context.get('unit')
        space_to_use = context.get('space_to_use')
        domain_tests = context.get('domain_tests')
        if not all([unit, space_to_use]):
            return False
            
        algorithm = unit.get_prop('algorithm')
        added_some = []
        
        for sibling in space_to_use:
            sibling_apps = sibling.get_prop('applications', [])
            
            for app in sibling_apps:
                args = app.get('args', [])
                if not args:
                    continue
                
                # Skip if already tried
                if any(args == existing.get('args') for existing in unit.get_prop('applications', [])):
                    continue
                    
                # Test domain constraints
                if not all(test(arg) for test, arg in zip(domain_tests, args)):
                    continue
                    
                # Try applying algorithm
                try:
                    result = algorithm(*args)
                    unit.add_to_prop('applications', {'args': args, 'result': result})
                    if sibling not in added_some:
                        added_some.append(sibling)
                except Exception as e:
                    logger.warning(f"Failed to apply {unit.name} to {args}: {e}")
                    
        context['added_some'] = added_some
        return bool(added_some)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print units with shared applications."""
        unit = context.get('unit')
        added_some = context.get('added_some')
        if not all([unit, added_some]):
            return False
            
        logger.info(f"{unit.name}'s algorithm has been run on new data upon which "
                   f"these have already been run: {[u.name for u in added_some]}")
        logger.info(f"We will sometime look for connections between {unit.name} "
                   f"and each of those other operations.")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks to investigate connections."""
        unit = context.get('unit')
        added_some = context.get('added_some')
        if not all([unit, added_some]):
            return False
            
        for sibling in added_some:
            task = {
                'priority': (unit.worth_value() + sibling.worth_value() + 
                           rule.worth_value()) // 3,
                'unit': unit,
                'slot': 'conjectures',
                'reasons': [
                    f"{unit.name} has now been run on the same data as {sibling.name}, "
                    "and we should investigate any patterns connecting them"
                ],
                'supplemental': {
                    'credit_to': ['h20'],
                    'involved_units': [sibling.name]
                }
            }
            rule.task_manager.add_task(task)
            
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [f"{len(added_some)} units may have connections "
                                   "to current one"]
        context['task_results'] = task_results
        
        return True