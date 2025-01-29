"""H8 heuristic implementation: Find application-instances from generalizations.

This heuristic looks for applications of a unit by checking existing generalizations that have valid 
applications which could also apply to this unit.
"""
import logging
from typing import Any, Dict, List, Optional
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def init_task_results(context: Dict[str, Any]) -> Dict[str, Any]:
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

def get_algorithm(unit) -> Optional[Any]:
    """Get the first available algorithm from a unit's algorithm slots.
    
    Checks multiple algorithm slots in order of preference.
    
    Args:
        unit: Unit to check for algorithms
        
    Returns:
        First found algorithm or None
    """
    # Check slots in precedence order
    for alg_slot in ['algorithm', 'fast-alg', 'iterative-alg', 'recursive-alg', 'unitized-alg']:
        alg = unit.get_prop(alg_slot)
        if alg:
            return alg
    return None 

def get_generalizations(unit, task_manager) -> List[Any]:
    """Get generalizations of a unit including ISA hierarchy.
    
    Args:
        unit: Unit to get generalizations for
        task_manager: Task manager for registry access
        
    Returns:
        List of generalization units
    """
    generalizations = set()
    
    # Direct generalizations
    gen_names = unit.get_prop('generalizations', [])
    for name in gen_names:
        gen_unit = task_manager.unit_registry.get_unit(name)
        if gen_unit:
            generalizations.add(gen_unit)
            
    # Parent category examples from ISA
    isa_names = unit.get_prop('isa', [])
    for name in isa_names:
        isa_unit = task_manager.unit_registry.get_unit(name) 
        if isa_unit:
            for ex_name in isa_unit.get_prop('examples', []):
                ex_unit = task_manager.unit_registry.get_unit(ex_name)
                if ex_unit:
                    generalizations.add(ex_unit)
                    
    return list(generalizations)

def get_domain_tests(unit) -> List[Any]:
    """Get domain test functions from unit's domain property.
    
    Args:
        unit: Unit to get domain tests for
        
    Returns:
        List of test functions
    """
    domain = unit.get_prop('domain', [])
    if not domain:
        return []
        
    # Get test functions for each domain constraint
    tests = []
    for dom in domain:
        if isinstance(dom, str):
            # Named type
            tests.append(lambda x, t=dom: isinstance(x, type(t)))
        else:
            # Assume test function
            tests.append(dom)
            
    return tests

def setup_h8(heuristic) -> None:
    """Configure H8: Find applications by checking generalizations.
    
    Args:
        heuristic: Heuristic to configure
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find application-instances of a unit, and it has "
        "an algorithm, THEN look over instances of generalizations of the unit, and "
        "see if any of them are valid application-instances of this as well")
    heuristic.set_prop('abbrev', "Find applics by checking generalizations")
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_potentially_relevant(rule, context: Dict[str, Any]) -> bool:
        """Check if we can find applications from generalizations.
        
        Args:
            rule: Rule being executed
            context: Current execution context
            
        Returns:
            bool: True if rule is potentially relevant
        """
        task = context.get('task')
        logger.debug(f"H8 task: {task}")

        if not task:
            logger.debug("H8: No task in context")
            return False
            
        logger.debug(f"H8 task type: {task.task_type}, supplemental: {task.supplemental}")

        # Must be a find_applications task and target applications slot
        if task.task_type != 'find_applications' or task.slot_name != 'applications': 
            logger.debug(f"H8: Wrong task type or slot: {task.task_type} {task.slot_name}")
            return False

        # Initialize task results
        init_task_results(context)
        
        # Get unit and algorithm
        unit = context.get('unit')
        if not unit:
            logger.debug("H8: No unit in context")
            return False
            
        algorithm = get_algorithm(unit)
        if not algorithm:
            logger.debug("H8: No algorithm available")
            return False
            
        # Store for compute phase
        context['algorithm'] = algorithm
        
        # Get and filter generalizations 
        generalizations = get_generalizations(unit, rule.task_manager)
        unit_arity = unit.get_prop('arity')
        
        space_to_use = []
        for gen_unit in generalizations:
            # Match arity and has applications
            if (gen_unit.get_prop('arity') == unit_arity and 
                gen_unit.get_prop('applications')):
                space_to_use.append(gen_unit)
                
        if not space_to_use:
            logger.debug("H8: No valid generalizations found")
            return False
            
        context['space_to_use'] = space_to_use
        logger.debug("H8 accepting applications task")
        return True

    @rule_factory 
    def then_compute(rule, context: Dict[str, Any]) -> bool:
        """Try to apply algorithm to examples from generalizations.
        
        Args:
            rule: Rule being executed
            context: Current execution context
            
        Returns:
            bool: True if any applications were found and added
        """
        logger.debug("H8 then_compute starting")
        
        # Get required context
        unit = context.get('unit')
        algorithm = context.get('algorithm')
        space_to_use = context.get('space_to_use')
        
        if not all([unit, algorithm, space_to_use]):
            logger.debug("H8: Missing required context")
            return False
            
        # Track current and new applications    
        current_apps = unit.get_prop('applications', [])
        new_apps = []
        domain_tests = get_domain_tests(unit)
        
        # Process each generalization
        for gen_unit in space_to_use:
            gen_apps = gen_unit.get_prop('applications', [])
            for app in gen_apps:
                # Skip if missing args
                args = app.get('args', [])
                if not args:
                    continue
                    
                # Skip if already known
                app_key = tuple(args)
                if app_key in [tuple(a.get('args', [])) for a in current_apps]:
                    continue
                    
                # Validate domain constraints
                valid_args = True
                for test, arg in zip(domain_tests, args):
                    try:
                        if test and not test(arg):
                            valid_args = False
                            break
                    except Exception as e:
                        logger.warning(f"Domain test failed for {arg}: {e}")
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
                        'worth': app.get('worth', 500),  # Inherit worth from generalization
                        'source': gen_unit.name  # Track source for debugging
                    })
                    logger.debug(f"H8: Found application {args} -> {result} from {gen_unit.name}")
                except Exception as e:
                    logger.warning(f"Failed to apply {unit.name} to {args}: {e}")
                    
        if not new_apps:
            logger.debug("H8: No new applications found")
            return False
            
        # Update unit and results
        current_apps.extend(new_apps)
        unit.set_prop('applications', current_apps)
        
        task_results = init_task_results(context)
        task_results['status'] = 'completed'
        task_results['success'] = True
        task_results['modified_units'].append(unit)
        task_results['new_values'] = {
            'unit': unit.name,
            'slot': 'applications',
            'values': new_apps,
            'description': f"Found {len(new_apps)} applications from generalizations"
        }
        
        logger.info(f"H8: Added {len(new_apps)} applications to {unit.name}")
        return True

    # Register rule functions
    heuristic.set_prop('if_potentially_relevant', if_potentially_relevant)
    heuristic.set_prop('then_compute', then_compute)