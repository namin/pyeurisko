"""H8 heuristic implementation: Find applications through generalizations."""
from typing import Any, Dict, List
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h8(heuristic) -> None:
    """Configure H8: Find applications by examining generalizations."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find application-instances of a unit, and it has "
        "an algorithm, THEN look over instances of generalizations of the unit, "
        "and see if any of them are valid application-instances of this as well.")
    heuristic.set_prop('abbrev', "Applications (u) may be found against Applications (genl (u))")

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Verify task is for finding applications."""
        task = context.get('task')
        unit = context.get('unit')
        if not task or not unit:
            return False

        if task.get('task_type') != 'find_applications':
            return False

        # Store algorithm for later use
        algorithm = unit.get_prop('algorithm')
        if not algorithm:
            return False
            
        context['algorithm'] = algorithm
        return True

    @rule_factory
    def then_compute(rule, context):
        """Find and verify applications from generalizations."""
        unit = context.get('unit')
        algorithm = context.get('algorithm')
        
        if not all([unit, algorithm]):
            return False

        # Get applications from generalizations
        new_applications = []
        generalizations = unit.get_prop('generalizations', [])
        
        for gen_name in generalizations:
            gen = rule.unit_registry.get_unit(gen_name)
            if not gen:
                continue
                
            gen_apps = gen.get_prop('applications', [])
            if not gen_apps:
                continue
                
            # Try each application from this generalization
            for app in gen_apps:
                args = app.get('args', [])
                if not unit.has_application(args):
                    try:
                        result = algorithm(*args)
                        new_applications.append({
                            'args': args,
                            'result': result,
                            'from_unit': gen_name
                        })
                    except Exception as e:
                        logger.debug(
                            f"Failed to apply {unit.name} to args from "
                            f"{gen_name}: {e}"
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

        # Group applications by source
        by_source = {}
        for app in new_apps:
            source = app.get('from_unit', 'unknown')
            by_source.setdefault(source, []).append(app)

        logger.info(
            f"\nFound {len(new_apps)} new applications for {unit.name} "
            f"from generalizations:"
        )

        for source, apps in by_source.items():
            logger.info(f"- {len(apps)} from {source}")
            for app in apps:
                logger.info(
                    f"  * Applied to {app['args']}, got {app['result']}"
                )

        return True