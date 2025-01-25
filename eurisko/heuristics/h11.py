"""H11 heuristic implementation: Find applications from domain examples.

This heuristic finds applications of a unit by taking examples from its domain and 
running the unit's algorithm on them. If the unit has multiple domain components, it 
takes combinations of examples to find valid applications.
"""
from typing import Any, Dict, List
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h11(heuristic) -> None:
    """Configure H11: Find applications from domain examples."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find application-instances of a unit f, and it "
        "has an Algorithm for computing its values, and it has a Domain, THEN "
        "choose examples of its domain component/s, and run the alg for f on such inputs")
    heuristic.set_prop('abbrev', "Apply algorithm to domain examples")
    heuristic.set_prop('arity', 1)
    
    # Set record counts from original
    heuristic.set_prop('then_compute_record', (2296694, 66))
    heuristic.set_prop('then_print_to_user_record', (47517, 66))
    heuristic.set_prop('overall_record', (2369179, 66))
    heuristic.set_prop('then_compute_failed_record', (1319487, 23))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're working on an applications task."""
        task = context.get('task')
        return task and task.get('task_type') == 'find_applications'

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit has algorithm and domain."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Need algorithm and domain
        if not unit.get_prop('algorithm'):
            return False
            
        domain_names = unit.get_prop('domain')
        if not domain_names:
            return False
            
        # Store for later use
        context['registry'] = heuristic.unit_registry
        context['domain_names'] = domain_names
        return True

    def print_results(context: Dict[str, Any]) -> bool:
        """Print the applications found."""
        unit = context.get('unit')
        new_values = context.get('task_results', {}).get('new_values', [])
        if not unit or not new_values:
            return False
        
        logger.info(f"\nFound {len(new_values)} new applications for {unit.name}")
        logger.debug(f"Applications: {new_values}")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find applications by applying algorithm to domain examples."""
        unit = context.get('unit')
        registry = context.get('registry')
        domain_names = context.get('domain_names')
        if not all([unit, registry, domain_names]):
            return False
            
        # Get algorithm
        algorithm = unit.get_prop('algorithm')
        
        # Get domain examples
        domain_examples = []
        for name in domain_names:
            domain_unit = registry.get_unit(name)
            if not domain_unit:
                continue
                
            examples = domain_unit.get_prop('examples') or []
            if not examples:
                continue
                
            domain_examples.append(examples)
            
        # Must have examples for each domain
        if len(domain_examples) != len(domain_names):
            return False
            
        # Track applications
        new_values = []
        current_apps = unit.get_prop('applications') or []
        known_apps = {str(app) for app in current_apps}
        
        # Try single domain case first
        if len(domain_examples) == 1:
            examples = domain_examples[0]
            for example in examples:
                args = [example]
                app = apply_to_args(args, algorithm)
                if app and str(app) not in known_apps:
                    new_values.append(app)
                    known_apps.add(str(app))
                    
        # Handle multiple domain case
        else:
            import itertools
            for args in itertools.product(*domain_examples):
                app = apply_to_args(list(args), algorithm)
                if app and str(app) not in known_apps:
                    new_values.append(app)
                    known_apps.add(str(app))
        
        # Update results if we found any
        if new_values:
            if 'task_results' not in context:
                context['task_results'] = {}
            context['task_results']['new_values'] = new_values
            
            # Add to unit's applications
            current_apps.extend(new_values)
            unit.set_prop('applications', current_apps)
            
        return bool(new_values)

    def apply_to_args(args: List[Any], algorithm: callable) -> Dict[str, Any]:
        """Apply algorithm to arguments and format result."""
        try:
            if len(args) == 1:
                result = algorithm(args[0])
            else:
                result = algorithm(*args)
                
            return {
                'args': args,
                'result': result
            }
        except:
            return None

    # Configure the heuristic
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)