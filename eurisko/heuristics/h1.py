"""H1 heuristic implementation: Specialize sometimes-useful actions."""
from typing import Any, Dict
from ..units import Unit
from ..tasks.task import Task
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h1(heuristic) -> None:
    """Configure H1: Specialize sometimes-useful actions."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 724)
    heuristic.set_prop('english', 
        "IF an op F (e.g., a mathematical function, a heuristic, etc.) has had some good "
        "applications, but over 4/5 are bad, THEN conjecture that some Specializations "
        "of F may be superior to F, and add tasks to specialize F to the Agenda.")
    heuristic.set_prop('abbrev', "Specialize a sometimes-useful action")
    
    # Initialize record properties as functions
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_conjecture_record', record_func)
    heuristic.set_prop('then_add_to_agenda_record', record_func)
    heuristic.set_prop('then_print_to_user_record', record_func)
    heuristic.set_prop('overall_record', record_func)

    @rule_factory
    def if_potentially_relevant(rule, context):
        logger.info(f"H1 checking potential relevance for unit {context.get('unit', 'no_unit')}, looking for applications")
        unit = context.get('unit')
        if not unit:
            logger.info("H1 no unit in context")
            return False
        applications = unit.get_prop('applications')
        if not applications:
            logger.info(f"H1 no applications for {unit.name}")
            return False
            
        logger.info(f"H1 found {len(applications)} applications for {unit.name}")
        return True
        
    @rule_factory
    def if_truly_relevant(rule, context):
        logger.info(f"H1 checking true relevance for unit {context.get('unit', 'no_unit')}, needs good/bad apps ratio")
        unit = context.get('unit')
        if not unit:
            logger.info("H1 no unit in context")
            return False
            
        # Get applications
        applications = unit.get_prop('applications')
        if not applications:
            logger.info(f"H1 no applications for {unit.name}")
            return False
            
        # Count good vs total applications
        total_count = len(applications)
        good_count = sum(1 for app in applications if app.get('worth', 0) >= 800)
        
        if total_count == 0:
            logger.info(f"H1 no valid applications for {unit.name}")
            return False
            
        # Need at least one good application
        if good_count == 0:
            logger.info(f"H1 no good applications for {unit.name}")
            return False
            
        # Store fraction for use in conjecture
        fraction = good_count / total_count
        context['fraction'] = fraction
            
        # Check not subsumed
        if unit.get_prop('subsumed_by'):
            logger.info(f"H1 unit {unit.name} is subsumed")
            return False
            
        # More than 4/5 should be bad (i.e., fraction good < 0.2)
        if fraction > 0.2:
            logger.info(f"H1 too many good applications ({fraction:.2f}) for {unit.name}")
            return False
            
        logger.info(f"H1 unit {unit.name} is relevant with {fraction:.2f} good fraction")
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        logger.info(f"H1 printing user message for {context.get('unit', 'no_unit')}")
        unit = context.get('unit')
        conjec = context.get('conjecture')
        if not unit or not conjec:
            logger.info("H1 missing unit or conjecture for user message")
            return False
            
        logger.info(f"\n{conjec}:\nSince some specializations of {unit.name} are quite "
                   f"valuable, but over four-fifths are trash, EURISKO has recognized "
                   f"the value of finding new concepts similar to -- but more specialized "
                   f"than -- {unit.name}, and (to that end) has added a new task to the "
                   f"agenda to find such specializations.")
        return True

    @rule_factory
    def then_conjecture(rule, context):
        logger.info(f"H1 creating conjecture about {context.get('unit', 'no_unit')}")
        unit = context.get('unit')
        system = context.get('system')
        fraction = context.get('fraction', 0)
        
        if not unit or not system:
            logger.info(f"H1 missing unit={bool(unit)} or system={bool(system)}")
            return False
        
        # Create new conjecture
        conjec_name = system.new_name('conjec')
        conjec = system.create_unit(conjec_name, 'proto-conjec')
        if not conjec:
            logger.info("H1 failed to create conjecture unit")
            return False
        
        english = (f"Specializations of {unit.name} may be more useful than it is, "
                  f"since it has some good instances but many more poor ones. "
                  f"({(1.0 - fraction)*100:.1f}% are losers)")
        
        conjec.set_prop('english', english)
        conjec.set_prop('abbrev', 
            f"{unit.name} sometimes wins, usually loses, so specializations may win big")
        
        # Calculate worth based on fraction and average worths
        worth = int(min(1000, (0.9 - fraction) * 1000))
        conjec.set_prop('worth', worth)
        
        # Add to conjectures list
        if not system.add_conjecture(conjec):
            logger.info("H1 failed to add conjecture to system")
            return False
            
        context['conjecture'] = conjec
        logger.info(f"H1 created conjecture {conjec_name}")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        logger.info(f"H1 adding task for {context.get('unit', 'no_unit')}")
        
        unit = context.get('unit')
        system = context.get('system')
        conjec = context.get('conjecture')
        task_mgr = context.get('task_manager')
        
        if not all([unit, system, conjec, task_mgr]):
            logger.info(f"H1 missing: unit={bool(unit)}, system={bool(system)}, conjec={bool(conjec)}, task_mgr={bool(task_mgr)}")
            return False
            
        task = Task(
            priority=unit.get_prop('worth', 500),
            unit_name=unit.name,
            slot_name='specializations',
            reasons=[conjec.name],
            task_type='specialization',
            supplemental={
                'credit_to': ['h1'],
                'task_type': 'specialization'
            }
        )
        
        task_mgr.add_task(task)
        logger.info(f"H1 added task to specialize {unit.name}")
        
        if 'task_results' in context:
            results = context['task_results']
            if 'new_tasks' not in results:
                results['new_tasks'] = []
            results['new_tasks'].append(f"Specializing {unit.name} based on {conjec.name}")
        
        return True