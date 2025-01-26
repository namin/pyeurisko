"""H8 heuristic implementation: Find application-instances from generalizations."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h8(heuristic) -> None:
    """Configure H8: Find applications by checking generalizations."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to find application-instances of a unit, and it has "
        "an algorithm, THEN look over instances of generalizations of the unit, and "
        "see if any of them are valid application-instances of this as well")
    heuristic.set_prop('abbrev', "Find applics by checking generalizations")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_compute_record', record_func)
    heuristic.set_prop('then_print_to_user_record', record_func)
    heuristic.set_prop('overall_record', record_func)
    heuristic.set_prop('then_compute_failed_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we can find applications from generalizations."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('slot') != 'applications':
            return False
            
        # Get algorithm and generalizations
        algorithm = unit.get_prop('algorithm')
        generalizations = unit.get_prop('generalizations', [])
        if not algorithm or not generalizations:
            return False
            
        # Filter generalizations to same arity
        unit_arity = unit.get_prop('arity')
        space_to_use = []
        for gen in generalizations:
            gen_unit = rule.unit_registry.get_unit(gen)
            if gen_unit and gen_unit.get_prop('arity') == unit_arity:
                space_to_use.append(gen_unit)
                
        context['algorithm'] = algorithm
        context['space_to_use'] = space_to_use
        return bool(space_to_use)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print found applications."""
        unit = context.get('unit')
        new_values = context.get('new_values', [])
        if not unit or not new_values:
            return False
            
        logger.info(f"\nInstantiated {unit.name}; found {len(new_values)} applications")
        logger.info(f"    Namely: {new_values}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Try to apply algorithm to examples from generalizations."""
        unit = context.get('unit')
        algorithm = context.get('algorithm')
        space_to_use = context.get('space_to_use')
        if not all([unit, algorithm, space_to_use]):
            return False
            
        # Track current applications
        current_apps = unit.get_prop('applications', [])
        new_apps = []
        domain_tests = unit.get_prop('domain_tests', [])
        
        # Check applications from each generalization
        for gen_unit in space_to_use:
            gen_apps = gen_unit.get_prop('applications', [])
            for app in gen_apps:
                # Skip if already known
                args = app.get('args', [])
                if not args:
                    continue
                    
                app_key = tuple(args)
                if app_key in [tuple(a.get('args', [])) for a in current_apps]:
                    continue
                    
                # Check domain constraints
                valid_args = True
                for test, arg in zip(domain_tests, args):
                    if not test(arg):
                        valid_args = False
                        break
                        
                if not valid_args:
                    continue
                    
                # Try applying algorithm
                try:
                    result = algorithm(*args)
                    new_apps.append({
                        'args': args,
                        'result': result
                    })
                except Exception as e:
                    logger.warning(f"Failed to apply {unit.name} to {args}: {e}")
                    
        if new_apps:
            # Update unit applications
            unit.set_prop('applications', current_apps + new_apps)
            context['new_values'] = new_apps
            
            # Update task results 
            task_results = context.get('task_results', {})
            task_results['new_values'] = {
                'unit': unit.name,
                'slot': 'applications',
                'values': new_apps,
                'description': f"Found {len(new_apps)} applications by examining "
                             f"applications of {len(space_to_use)} generalizations"
            }
            context['task_results'] = task_results
            
        return bool(new_apps)