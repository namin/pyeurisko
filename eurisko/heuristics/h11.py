"""H11 heuristic implementation: Find applications using domain examples."""
from typing import Any, Dict
import logging
import random
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h11(heuristic) -> None:
    """Configure H11: Find applications by running algorithm on domain."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to find application-instances of a unit f, and it "
        "has an Algorithm for computing its values, and it has a Domain, THEN choose "
        "examples of its domain component/s, and run the alg for f on such inputs")
    heuristic.set_prop('abbrev', "Find applications using domain examples")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)
    heuristic.set_prop('then_compute_failed_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we can run algorithm on domain examples."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]) or task.get('slot') != 'applications':
            return False
            
        algorithm = unit.get_prop('algorithm')
        domain = unit.get_prop('domain', [])
        if not algorithm or not domain:
            return False
            
        context['algorithm'] = algorithm
        context['space_to_use'] = domain
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print application counts."""
        unit = context.get('unit')
        new_values = context.get('new_values', [])
        if not all([unit, new_values]):
            return False
            
        logger.info(f"\nFound {len(new_values)} applications")
        logger.info(f"    Namely: {new_values}")
        return True

    @rule_factory 
    def then_compute(rule, context):
        """Run algorithm on domain examples."""
        unit = context.get('unit')
        algorithm = context.get('algorithm')
        domain = context.get('space_to_use')
        if not all([unit, algorithm, domain]):
            return False
            
        current_apps = unit.get_prop('applications', [])
        domain_tests = [d.get_prop('definition') for d in domain]
        n_tried = 0
        new_apps = []
        max_tries = 50
        
        def try_apply(args):
            """Try to apply algorithm to args."""
            app_key = tuple(args)
            if app_key in [tuple(a.get('args', [])) for a in current_apps]:
                return False
                
            # Check domain constraints
            if not all(test(arg) for test, arg in zip(domain_tests, args)):
                return False
                
            try:
                result = algorithm(*args)
                new_apps.append({
                    'args': args,
                    'result': result
                })
                return True
            except Exception as e:
                logger.warning(f"Failed to apply {unit.name} to {args}: {e}")
                return False
        
        match len(domain_tests):
            case 0:  # No domain constraints
                for _ in range(100):
                    if try_apply([]):
                        n_tried += 1
                    
            case 1:  # Single domain
                dom_unit = domain[0]
                if dom_unit.get_prop('generator'):
                    for _ in range(200):
                        example = dom_unit.generate_example()
                        if example and try_apply([example]):
                            n_tried += 1
                else:
                    for _ in range(max_tries):
                        args = [random.choice(dom_unit.get_prop('examples', []))]
                        if args[0] and try_apply(args):
                            n_tried += 1
                            
            case _:  # Multiple domains
                for _ in range(max_tries):
                    args = [random.choice(d.get_prop('examples', [])) 
                           for d in domain]
                    if all(args) and try_apply(args):
                        n_tried += 1
        
        if new_apps:
            unit.set_prop('applications', current_apps + new_apps)
            context['new_values'] = new_apps
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = {
                'unit': unit.name,
                'applications': new_apps,
                'description': f"Found {len(new_apps)} applications by running algorithm on "
                             f"{n_tried} domain examples"
            }
            context['task_results'] = task_results
            
            # Update rarity statistics
            total_success = len(new_apps)
            total_tries = n_tried
            rarity = unit.get_prop('rarity', {'success': 0, 'tries': 0})
            rarity['success'] += total_success
            rarity['tries'] += total_tries
            unit.set_prop('rarity', rarity)
            
        return bool(new_apps)