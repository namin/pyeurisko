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
        """Check if we're looking for applications with algorithm and domain."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('task_type') != 'find_applications':
            return False
            
        # Need both algorithm and domain specification
        algorithm = unit.get_prop('algorithm')
        domain = unit.get_prop('domain')
        
        if not algorithm or not domain:
            return False
            
        context['algorithm'] = algorithm
        context['domain'] = domain
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find applications by running algorithm on domain examples."""
        unit = context.get('unit')
        algorithm = context.get('algorithm')
        domain_units = context.get('domain')
        
        if not all([unit, algorithm, domain_units]):
            return False
            
        # Get domain tests from domain units
        domain_tests = []
        for domain_unit in domain_units:
            domain_def = heuristic.unit_registry.get_unit(domain_unit)
            if domain_def and domain_def.get_prop('definition'):
                domain_tests.append(domain_def.get_prop('definition'))
            
        if len(domain_tests) != len(domain_units):
            logger.warning(f"Missing domain definitions for {unit.name}")
            return False
            
        # Track new applications found
        new_applications = []
        start_time = time.time()
        max_time = 30  # Maximum seconds to spend
        attempts = 0
        max_attempts = 100
        
        def check_timeout():
            return time.time() - start_time > max_time
            
        # Handle different domain arities
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
                    logger.warning(f"Failed to apply algorithm with no args: {e}")
                    
        elif len(domain_tests) == 1:
            # Unary operation
            domain_unit = heuristic.unit_registry.get_unit(domain_units[0])
            if not domain_unit:
                return False
                
            # Try generator if available
            generator = domain_unit.get_prop('generator')
            if generator and callable(generator):
                for _ in range(200):
                    if check_timeout():
                        break
                        
                    try:
                        arg = generator()
                        if not domain_tests[0](arg):
                            continue
                            
                        if unit.has_application([arg]):
                            continue
                            
                        result = algorithm(arg)
                        new_applications.append({
                            'args': [arg],
                            'result': result
                        })
                    except Exception as e:
                        logger.debug(f"Failed generator application: {e}")
                        
            # Otherwise use examples
            else:
                examples = domain_unit.get_prop('examples') or []
                for example in examples:
                    if check_timeout():
                        break
                        
                    if not domain_tests[0](example):
                        continue
                        
                    if unit.has_application([example]):
                        continue
                        
                    try:
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
                
                # Get random examples from each domain
                for domain_unit_name in domain_units:
                    domain_unit = heuristic.unit_registry.get_unit(domain_unit_name)
                    if not domain_unit:
                        valid = False
                        break
                        
                    examples = domain_unit.get_prop('examples')
                    if not examples:
                        valid = False
                        break
                        
                    args.append(random.choice(examples))
                    
                if not valid:
                    continue
                    
                # Check domain constraints
                if not all(test(arg) for test, arg in zip(domain_tests, args)):
                    continue
                    
                # Skip if we already know this application
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
            return True
            
        return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)