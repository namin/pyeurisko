"""H8 heuristic implementation: Find applications through generalizations."""
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

def setup_h8(heuristic) -> None:
    """Configure H8: Find applications by examining generalizations."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find application-instances of a unit, and it has "
        "an algorithm, THEN look over instances of generalizations of the unit, "
        "and see if any of them are valid application-instances of this as well.")
    heuristic.set_prop('abbrev', "Applics (u) may be found against Applics (genl (u))")

    def check_task_relevance(context: Dict[str, Any]) -> bool:
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

    def get_applications_from_generalizations(
        unit: Any,
        registry: Any
    ) -> List[Dict[str, Any]]:
        """Get applications from unit's generalizations."""
        applications = []
        generalizations = unit.get_prop('generalizations', [])
        
        for gen_name in generalizations:
            gen = registry.unit_registry.get_unit(gen_name)
            if gen:
                gen_apps = gen.get_prop('applications', [])
                if gen_apps:
                    for app in gen_apps:
                        applications.append({
                            'args': app.get('args', []),
                            'source': gen_name,
                            'from_unit': gen_name
                        })
                        
        return applications

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find and verify applications from generalizations."""
        unit = context.get('unit')
        algorithm = context.get('algorithm')
        registry = context.get('registry')
        
        if not all([unit, algorithm, registry]):
            return False

        # Get applications from generalizations
        gen_applications = get_applications_from_generalizations(unit, registry)
        if not gen_applications:
            return False

        # Track successful new applications 
        new_applications = []

        # Try each application
        for app in gen_applications:
            args = app.get('args', [])
            if not unit.has_application(args):
                try:
                    result = algorithm(*args)
                    new_applications.append({
                        'args': args,
                        'result': result,
                        'from_unit': app['from_unit']
                    })
                except Exception as e:
                    logger.debug(
                        f"Failed to apply {unit.name} to args from "
                        f"{app['source']}: {e}"
                    )

        if new_applications:
            context['task_results'] = context.get('task_results', {})
            context['task_results']['new_values'] = new_applications
            return True

        return False

    def print_to_user(context: Dict[str, Any]) -> bool:
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

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_task_relevance)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)