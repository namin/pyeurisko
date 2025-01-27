"""H5 heuristic implementation."""
import random
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h5(heuristic):
    heuristic.set_prop('worth', 151)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN randomly select which slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular slots of u to specialize")
    heuristic.set_prop('arity', 1)
    heuristic.set_prop('subsumes', ['h3'])
    heuristic.set_prop('subsumed_by', ['h5-criterial', 'h5-good'])

    @rule_factory 
    def if_potentially_relevant(rule, context):
        task = context.get('task')
        unit = context.get('unit')
        if not task or not unit:
            logger.debug("H5 if_potentially_relevant: Missing task or unit")
            return False
            
        task_type = task.get('task_type')
        logger.debug(f"H5 if_potentially_relevant: Checking task type {task_type} for unit {unit.name}")
            
        if task_type != 'specialization':
            logger.debug(f"H5 if_potentially_relevant: Wrong task type {task_type}")
            return False
            
        supplemental = task.get('supplemental', {})
        logger.debug(f"H5 if_potentially_relevant: Supplemental {supplemental}")
        if 'slot_to_change' in supplemental:
            logger.debug("H5 if_potentially_relevant: slot_to_change already selected")
            return False
            
        logger.debug(f"H5 if_potentially_relevant: Task relevant for {unit.name}")
        return True

    @rule_factory
    def if_working_on_task(rule, context):
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            logger.debug("H5: No unit or task")
            return False

        logger.debug(f"H5: Looking at slots for {unit.name}, context: {context}")
        specializable_slots = []
        for key, value in unit.properties.items():
            if value is None or (isinstance(value, (list, dict)) and not value):
                continue
            if key in ['creditors', 'worth', 'specializations', 'generalizations']:
                continue
            if isinstance(value, (list, dict, str, int, float, bool)):
                specializable_slots.append(key)
                logger.debug(f"H5: Found specializable slot {key} with value type {type(value)}")

        if not specializable_slots:
            logger.debug(f"H5: No specializable slots for {unit.name}")
            return False
            
        logger.debug(f"H5: Found specializable slots for {unit.name}: {specializable_slots}")
        context['specializable_slots'] = specializable_slots
        return True

    @rule_factory 
    def then_compute(rule, context):
        unit = context.get('unit')
        specializable_slots = context.get('specializable_slots', [])
        logger.debug(f"H5 then_compute starting for {unit.name}")
        logger.debug(f"H5 specializable slots: {specializable_slots}")
        if not unit or not specializable_slots:
            logger.debug("H5 then_compute: No unit or slots")
            return False

        important_slots = ['domain', 'range', 'isa', 'applics', 'applications'] 
        weighted_slots = []
        for slot in specializable_slots:
            weight = 3.0 if slot in important_slots else 1.0
            logger.debug(f"H5 slot {slot} given weight {weight}")
            weighted_slots.extend([slot] * int(weight * 10))

        num_slots = min(random.randint(1, 3), len(specializable_slots))
        selected_slots = random.sample(weighted_slots, num_slots)
        selected_slots = list(set(selected_slots))
        logger.debug(f"H5 selected slots: {selected_slots}")

        if not selected_slots:
            logger.debug("H5 then_compute: No slots selected")
            return False
            
        context['slots_to_change'] = selected_slots
        task_results = context.get('task_results', {})
        logger.debug(f"H5 then_compute: Current task_results {task_results}")
        task_results['slots_to_change'] = selected_slots
        task_results['status'] = 'slots_selected'
        context['task_results'] = task_results
        logger.debug(f"H5 then_compute: Updated task_results {task_results}")
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        slots = context.get('slots_to_change', [])
        if not slots:
            return False
            
        unit = context.get('unit')
        logger.info(f"\n{unit.name} will be specialized by specializing: {slots}")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        unit = context.get('unit')
        task = context.get('task')
        slots = context.get('slots_to_change', [])
        task_manager = rule.task_manager
        
        logger.debug(f"H5 then_add_to_agenda: Context dump:")
        logger.debug(f"  unit: {unit.name if unit else None}")
        logger.debug(f"  task: {task.get('task_type') if task else None}")
        logger.debug(f"  slots: {slots}")
        logger.debug(f"  task_manager: {task_manager is not None}")
        logger.debug(f"  task_results: {context.get('task_results')}")
        
        if not all([unit, task, slots, task_manager]):
            missing = []
            if not unit: missing.append('unit')
            if not task: missing.append('task')
            if not slots: missing.append('slots')
            if not task_manager: missing.append('task_manager')
            logger.debug(f"H5 then_add_to_agenda: Missing required values: {missing}")
            return False

        base_priority = task.get('priority', 500)
        tasks_added = 0
        
        for slot in slots:
            new_task = {
                'priority': int((base_priority + rule.worth_value()) / 2),
                'unit': unit.name,
                'slot': 'specializations',
                'task_type': 'specialization', 
                'reasons': [f"Specializing {slot} slot of {unit.name}"],
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h5']
                }
            }
            logger.debug(f"H5 adding task: {new_task}")
            task_manager.add_task(new_task)
            tasks_added += 1
            
        if tasks_added == 0:
            logger.debug("H5 then_add_to_agenda: No tasks added")
            return False
            
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [f"{tasks_added} slots to specialize"]
        task_results['status'] = 'completed'
        task_results['success'] = True
        context['task_results'] = task_results
        
        logger.debug(f"H5 successfully added {tasks_added} tasks")
        return True