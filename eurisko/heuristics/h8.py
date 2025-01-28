"""H8 heuristic implementation: Find application-instances from generalizations."""
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def init_task_results(context):
    """Initialize task results structure if needed."""
    if 'task_results' not in context:
        context['task_results'] = {
            'status': 'in_progress',
            'initial_unit_state': {},
            'new_units': [],
            'new_tasks': [],
            'modified_units': []
        }
    else:
        results = context['task_results']
        if 'new_units' not in results:
            results['new_units'] = []
        if 'new_tasks' not in results:
            results['new_tasks'] = []
        if 'modified_units' not in results:
            results['modified_units'] = []
    return context['task_results']

def get_algorithm(unit):
    """Get the first available algorithm from a unit's algorithm slots."""
    for alg_slot in ['fast-alg', 'iterative-alg', 'recursive-alg', 'unitized-alg']:
        alg = unit.get_prop(alg_slot)
        if alg:
            return alg
    return None

def get_domain_tests(unit):
    """Get domain test functions from unit's domain property."""
    domain = unit.get_prop('domain', [])
    if not domain:
        return []
        
    # For now just check types - could be expanded to more complex tests
    return [lambda x, t=t: isinstance(x, type(t)) for t in domain]

def setup_h8(heuristic):
    """Configure H8: Find applications by checking generalizations."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find application-instances of a unit, and it has "
        "an algorithm, THEN look over instances of generalizations of the unit, and "
        "see if any of them are valid application-instances of this as well")
    heuristic.set_prop('abbrev', "Find applics by checking generalizations")
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check if we can find applications from generalizations."""
        task = context.get('task')
        logger.debug(f"H8 task: {task}")

        if not task:
            logger.debug("H8: No task in context")
            return False
            
        logger.debug(f"H8 task type: {task.task_type}, supplemental: {task.supplemental}")

        # Must be a find_applications task
        if task.task_type != 'find_applications' and task.slot_name != 'applications':
            logger.debug(f"H8: Wrong task type or slot: {task.task_type} {task.slot_name}")
            return False

        # Initialize task results
        init_task_results(context)
        
        logger.debug("H8 accepting applications task")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Try to apply algorithm to examples from generalizations."""
        logger.debug("H8 then_compute starting")
        
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            logger.debug("H8: Missing unit or task")
            return False
            
        # Get algorithm
        algorithm = get_algorithm(unit)
        if not algorithm:
            logger.debug("H8: No algorithm available")
            return False
            
        # Get and filter generalizations
        generalizations = unit.get_prop('generalizations', [])
        unit_arity = unit.get_prop('arity')
        
        space_to_use = []
        for gen_name in generalizations:
            gen_unit = rule.unit_registry.get_unit(gen_name)
            if gen_unit and gen_unit.get_prop('arity') == unit_arity:
                space_to_use.append(gen_unit)
                
        if not space_to_use:
            logger.debug("H8: No valid generalizations found")
            return False
            
        # Track current applications
        current_apps = unit.get_prop('applications', [])
        new_apps = []
        domain_tests = get_domain_tests(unit)
        
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
                    if test and not test(arg):
                        valid_args = False
                        break
                        
                if not valid_args:
                    continue
                    
                # Try applying algorithm
                try:
                    result = algorithm(*args)
                    new_apps.append({
                        'args': args,
                        'result': result,
                        'worth': app.get('worth', 500)  # Inherit worth from generalization
                    })
                except Exception as e:
                    logger.warning(f"Failed to apply {unit.name} to {args}: {e}")
                    
        if not new_apps:
            logger.debug("H8: No new applications found")
            return False
            
        # Update unit applications
        current_apps.extend(new_apps)
        unit.set_prop('applications', current_apps)
        
        # Update task results
        task_results = init_task_results(context)
        task_results['status'] = 'completed'
        task_results['success'] = True
        task_results['modified_units'].append(unit)
        
        logger.info(f"H8: Found {len(new_apps)} new applications from generalizations")
        return True

    # Set the functions as properties on the heuristic
    heuristic.set_prop('if_potentially_relevant', if_potentially_relevant)
    heuristic.set_prop('then_compute', then_compute)
