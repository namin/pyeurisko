# Updating Heuristics for New Design

This document outlines how to update each heuristic to work with our new task management and unit creation system. The updates focus on standardizing how heuristics interact with task contexts and manage unit creation.

## Core Changes to Heuristic Structure

Each heuristic now needs to follow a standard pattern that includes proper initialization, context handling, and result tracking. The implementation includes:

1. A setup function that initializes the heuristic unit with the required properties
2. An if_working_on_task function that evaluates task context 
3. Action functions (then_*) that manipulate units and track results
4. A HeuristicRecord for tracking performance statistics

## H2: Kill Concepts That Produce Garbage

H2 requires minimal updates as it already works with the new system. Its current implementation properly checks task results for new units and manages unit deletion. Key functions remain:

    if_finished_working_on_task: Examines task results for garbage units
    then_compute: Identifies creators of garbage units
    then_delete_old_concepts: Removes low-worth units

## H3: Choose Slots for Specialization

H3 needs significant updates to work with the new context system:

    if_working_on_task: Update to check both task.slot_name and task.supplemental
    then_compute: Modify to use the task context for slot selection
    then_add_to_agenda: Update to include slot_to_change in task supplemental

The new version should coordinate with H6 by preparing appropriate slots for specialization.

## H4: Find Empirical Data About New Units

H4's update focuses on tracking unit creation:

    if_finished_working_on_task: Update to use task_results for new unit detection
    then_add_to_agenda: Modify to create application-finding tasks
    then_compute: Add to track application results in the task context

## H5: Random Slot Specialization

This heuristic family (H5, H5-criterial, H5-good) needs unified updates:

    if_working_on_task: Standardize slot selection logic
    then_compute: Update to use shared context for selected slots
    then_add_to_agenda: Ensure proper task creation for H6

## H6: Specialize Selected Slots

H6 is our reference implementation for the new design. Other heuristics should follow its pattern:

    if_working_on_task: Check task context for specialization requirements
    then_compute: Transform slot values appropriately
    then_define_new_concepts: Create and track new specialized units

## H7-H15: Analysis and Pattern Finding

These heuristics need updates to their core investigative functions:

    then_compute: Standardize result recording
    then_add_to_agenda: Update task creation patterns
    then_define_new_concepts: Align with new unit creation standards

## H16-H23: Creation and Modification

The creative heuristics require careful updates:

    then_compute: Ensure proper context usage for creative decisions
    then_define_new_concepts: Standardize unit creation process
    then_add_to_agenda: Update to maintain investigation chains

## Implementation Notes

When updating each heuristic:

1. Start by adding proper HeuristicRecord initialization in the setup function
2. Update condition checks to use standardized context access
3. Modify action functions to properly track unit creation and modification
4. Add detailed logging for debugging and performance analysis

## Testing Strategy

Each updated heuristic should be tested for:

1. Proper context handling during task execution
2. Correct unit creation and tracking
3. Appropriate task generation for further investigation
4. Performance metric recording

Tests should verify that heuristics maintain their original behavioral patterns while working within the new infrastructure.

## Migration Timeline

The heuristics should be updated in this order:

1. Finish testing H6 as the reference implementation
2. Update H5 family to coordinate with H6
3. Update H3-H4 for slot selection and empirical investigation
4. Update remaining heuristics in groups based on functionality

This order ensures that core unit creation and specialization capabilities are stable before updating more complex behaviors.