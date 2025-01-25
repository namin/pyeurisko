"""H11 heuristic implementation: Find applications by running algorithm on domain examples."""
from typing import Any, Dict, List, Callable
from ..unit import Unit
import logging
import random
import time

logger = logging.getLogger(__name__)

def setup_h11(heuristic) -> None:
    """Configure H11: Find applications using algorithm and domain."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we can find applications."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('task_type') != 'find_applications':
            return False
            
        # Verify algorithm exists
        algorithm = unit.get_prop('algorithm')
        if not callable(algorithm):
            return False
            
        # Verify domain exists
        domain = unit.get_prop('domain')
        if not domain:
            return False
            
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find applications by running algorithm on domain examples."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Get algorithm
        algorithm = unit.get_prop('algorithm')
        if not callable(algorithm):
            return False
            
        # Get domain units and their definitions
        domain_units = []
        domain_tests = []
        domain_names = unit.get_prop('domain') or []
        
        for domain_name in domain_names:
            domain_unit = heuristic.unit_registry.get_unit(domain_name)
            if not domain_unit:
                logger.warning(f"Domain unit {domain_name} not found")
                continue
                
            definition = domain_unit.get_prop('definition')
            if not callable(definition):
                logger.warning(f"No callable definition for domain {domain_name}")
                continue
                
            domain_units.append(domain_unit)
            domain_tests.append(definition)
            
        if len(domain_tests) != len(domain_names):
            logger.warning("Not all domain units have valid definitions")
            return False
            
        # Track new applications found
        new_applications = []
        start_time = time.time()
        max_time = 30  # Maximum seconds to spend
        max_attempts = 100
        attempts = 0
        
        def check_timeout():
            return time.time() - start_time > max_time
            
        # Handle different arities
        if len(domain_tests) == 0:
            # Nullary operation
            if not unit.has_application([]):
                try:
                    result = algorithm()
                    new_applications.append({
                        'args': [],
                        'result': result
                    })
                except Exception as e:
                    logger.debug(f"Failed nullary application: {e}")
                    
        elif len(domain_tests) == 1:
            # Unary operation
            domain_unit = domain_units[0]
            test = domain_tests[0]
            
            # Try generator if available
            generator = domain_unit.get_prop('generator')
            if callable(generator):
                for _ in range(200):
                    if check_timeout():
                        break
                        
                    try:
                        arg = generator()
                        if not test(arg):
                            continue
                            
                        if unit.has_application([arg]):
                            continue
                            
                        result = algorithm(arg)
                        new_applications.append({
                            'args': [arg],
                            'result': result
                        })
                    except Exception as e:
                        logger.debug(f"Failed generated application: {e}")
                        
            # Otherwise use examples
            examples = domain_unit.get_prop('examples') or []
            for example in examples:
                if check_timeout():
                    break
                    
                try:
                    if not test(example):
                        continue
                        
                    if unit.has_application([example]):
                        continue
                        
                    result = algorithm(example)
                    new_applications.append({
                        'args': [example],
                        'result': result
                    })
                except Exception as e:
                    logger.debug(f"Failed example application: {e}")
                    
        else:
            # Multi-argument operation
            while attempts < max_attempts and not check_timeout():
                attempts += 1
                args = []
                valid = True
                
                # Get example from each domain
                for domain_unit in domain_units:
                    examples = domain_unit.get_prop('examples') or []
                    if not examples:
                        valid = False
                        break
                    args.append(random.choice(examples))
                    
                if not valid:
                    continue
                    
                # Check domain constraints
                if not all(test(arg) for test, arg in zip(domain_tests, args)):
                    continue
                    
                # Skip if already known
                if unit.has_application(args):
                    continue
                    
                # Try applying algorithm
                try:
                    result = algorithm(*args)
                    new_applications.append({
                        'args': args,
                        'result': result
                    })
                except Exception as e:
                    logger.debug(f"Failed multi-arg application: {e}")
                    
        if new_applications:
            # Update unit's applications
            current_applications = unit.get_prop('applications') or []
            unit.set_prop('applications', current_applications + new_applications)
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = new_applications
            task_results['num_found'] = len(new_applications)
            task_results['attempts'] = attempts
            return True
            
        return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)