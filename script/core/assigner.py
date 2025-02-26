"""Core task assignment functionality."""

from typing import List, Dict, Tuple, Set
from core.models import Task, Assignment, AvailabilityData
from utils.time_utils import is_fully_available

def find_available_people(task: Task, availability_data: AvailabilityData) -> Set[int]:
    """Find all people who are available for the entire duration of a task.
    
    Args:
        task (Task): Task to find available people for
        availability_data (AvailabilityData): Availability information
        
    Returns:
        Set[int]: Set of person IDs who are available for the task
    """
    need_start, need_end = task.time_slot.split('-')
    available_people = set()
    
    # Get all people who are marked as available in any overlapping slot
    potential_people = set()
    for avail_slot, people in availability_data.availability.items():
        avail_start, avail_end = avail_slot.split('-')
        if ((avail_start <= need_start and avail_end > need_start) or 
            (avail_start < need_end and avail_end >= need_end) or 
            (avail_start >= need_start and avail_end <= need_end)):
            potential_people.update(people)
    
    # Verify full availability for each potential person
    for person in potential_people:
        if is_fully_available(person, need_start, need_end, availability_data.availability):
            available_people.add(person)
    
    return available_people

def assign_tasks(tasks: List[Task], availability_data: AvailabilityData) -> Tuple[List[Assignment], Dict[int, int]]:
    """Assign tasks based on availability and requirements.
    
    Args:
        tasks (List[Task]): List of tasks to assign
        availability_data (AvailabilityData): Availability information
        
    Returns:
        Tuple[List[Assignment], Dict[int, int]]: 
            - List of assignments
            - Dictionary mapping person IDs to number of assignments
    """
    assignments = []  # Store all assignments
    assigned_people = {}  # Track how many times each person is assigned
    
    # Process each task
    for task in tasks:
        # Find available people for this task
        available_people = find_available_people(task, availability_data)
        
        if not available_people:
            print(f"Warning: No one available for {task.duty_group} at {task.time_slot}")
            continue
        
        # Sort by number of existing assignments, then by S/N
        available_people = sorted(list(available_people), 
                               key=lambda x: (assigned_people.get(x, 0), x))
        
        # Make assignments
        assigned_to_slot = []
        for person in available_people:
            if len(assigned_to_slot) >= task.people_needed:
                break
            
            assigned_to_slot.append(person)
            assigned_people[person] = assigned_people.get(person, 0) + 1
        
        # Record the assignment
        if assigned_to_slot:
            assignments.append(Assignment(
                duty_group=task.duty_group,
                time_slot=task.time_slot,
                required=task.people_needed,
                assigned=assigned_to_slot,
                assigned_with_roles=[
                    f"S/N {p} ({availability_data.assigned_roles.get(p, '-')})" 
                    for p in assigned_to_slot
                ]
            ))
    
    return assignments, assigned_people 