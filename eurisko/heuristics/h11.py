"""H11 heuristic implementation: Find applications through domain examples."""
from typing import Any, Dict, List
import logging
import random
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h11(heuristic) -> None:
    """Configure H11: Find applications using domain examples.
    
    This heuristic finds applications for an operation by testing it with
    examples from its domain, enabling systematic discovery of valid
    applications through domain exploration.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find application-instances of a unit f, "
        "and it has an Algorithm for computing values, and it has a Domain, "
        "THEN choose examples of its domain components and run the algorithm.")
    heuristic.set_prop('abbrev', "Test algorithm on domain examples")

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Verify task is for finding applications."""
        task = context.get('task')
        unit = context.get('unit')
        
        if not task or not unit:
            return False
            
        if task.get('task_type') != 'find_applications':
            return False
            
        # Need algorithm and domain
        algorithm = unit.get_prop('algorithm')
        domain = unit.get_prop('domain', [])
        
        if not algorithm or not domain:
            return False
            
        context['algorithm'] = algorithm
        context['domain_names'] = domain
        return True

    @rule_factory
    def then_compute(rule, context):
        """Find applications using domain examples."""
        unit = context.get('unit')
        algorithm = context.get('algorithm')
        domain_names = context.get('domain_names', [])
        
        if not all([unit, algorithm, domain_names]):
            return False

        # Get example combinations from domain units
        examples_by_domain = {}
        for domain_name in domain_names:
            domain = rule.unit_registry.get_unit(domain_name)
            if not domain:
                continue
                
            domain_examples = domain.get_prop('examples', [])
            if not domain_examples:
                continue
                
            examples_by_domain[domain_name] = domain_examples
            
        # Need examples for all domains
        if len(examples_by_domain) != len(domain_names):
            return False

        # Generate random combinations
        combinations = []
        max_examples = 5
        for _ in range(max_examples):
            combo = []
            for domain_name in domain_names:
                example = random.choice(examples_by_domain[domain_name])
                combo.append(example)
            combinations.append(combo)

        # Track new applications
        new_applications = []

        # Test each combination
        for args in combinations:
            # Skip if we already know this application
            if unit.has_application(args):
                continue
                
            # Validate args against domain definitions
            valid = True
            for arg, domain_name in zip(args, domain_names):
                domain = rule.unit_registry.get_unit(domain_name)
                if not domain:
                    valid = False
                    break
                    
                definition = domain.get_prop('definition')
                if definition:
                    try:
                        if not definition(arg):
                            valid = False
                            break
                    except Exception:
                        valid = False
                        break
                        
            if not valid:
                continue

            # Try applying the algorithm
            try:
                result = algorithm(*args)
                new_applications.append({
                    'args': args,
                    'result': result,
                    'domains': domain_names
                })
            except Exception as e:
                logger.debug(
                    f"Failed to apply {unit.name} to {args}: {e}"
                )

        if new_applications:
            context['task_results'] = context.get('task_results', {})
            context['task_results']['new_values'] = new_applications
            return True

        return False

    @rule_factory
    def then_print_to_user(rule, context):
        """Report on applications found."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        
        if not unit or not task_results:
            return False
        
        new_apps = task_results.get('new_values', [])
        if not new_apps:
            return False

        logger.info(
            f"\nFound {len(new_apps)} new applications for {unit.name} "
            f"using domain examples:"
        )
        
        for app in new_apps:
            args = app['args']
            result = app['result']
            logger.info(f"  {args} -> {result}")
        
        return True