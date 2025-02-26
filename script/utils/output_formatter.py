"""Functions for formatting and saving task assignment results."""

import pandas as pd
from typing import List, Dict, Tuple

from core.models import Assignment, PersonInfo, AvailabilityData
from utils.time_utils import is_fully_available

def format_results(
    assignments: List[Assignment],
    assigned_people: Dict[int, int],
    availability_data: AvailabilityData
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Format results into DataFrames for output.
    
    Args:
        assignments (List[Assignment]): List of task assignments
        assigned_people (Dict[int, int]): Number of assignments per person
        availability_data (AvailabilityData): Availability information
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Person-centric and task-centric results
    """
    # Person-centric results
    person_results = []
    
    # Process all people, including those with no assignments
    for sn in sorted(availability_data.all_people):
        # Get all possible assignments (based on availability)
        possible_duties = []
        final_duties = []
        
        for assignment in assignments:
            # Check if person was actually assigned to this task
            if sn in assignment.assigned:
                final_duties.append(f"{assignment.duty_group} ({assignment.time_slot})")
            
            # Check if person could have done this task
            need_start, need_end = assignment.time_slot.split('-')
            if is_fully_available(sn, need_start, need_end, availability_data.availability):
                possible_duties.append(f"{assignment.duty_group} ({assignment.time_slot})")
        
        person_results.append(PersonInfo(
            sn=sn,
            name=availability_data.name_mapping[sn],
            role=availability_data.assigned_roles.get(sn, '-'),
            assignments_count=assigned_people.get(sn, 0),
            possible_tasks=sorted(set(possible_duties)),
            final_assignments=final_duties
        ))
    
    # Convert to DataFrame
    person_df = pd.DataFrame([
        {
            'S/N': p.sn,
            'Name': p.name,
            'Role': p.role,
            'Number of Assignments': p.assignments_count,
            'Possible Tasks': ', '.join(p.possible_tasks) if p.possible_tasks else 'No possible tasks',
            'Final Assignment': ', '.join(p.final_assignments) if p.final_assignments else 'No assignments'
        }
        for p in person_results
    ])
    
    # Task-centric results
    task_df = pd.DataFrame([
        {
            'Task': a.duty_group,
            'Time Slot': a.time_slot,
            'Required': a.required,
            'Assigned People': ', '.join(a.assigned_with_roles)
        }
        for a in assignments
    ])
    
    return person_df, task_df

def save_results_to_excel(person_results: pd.DataFrame, task_results: pd.DataFrame, output_path: str):
    """Save results to an Excel file with multiple sheets.
    
    Args:
        person_results (pd.DataFrame): Person-centric results
        task_results (pd.DataFrame): Task-centric results
        output_path (str): Path to save the Excel file
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sort person_results by S/N before saving
        person_results = person_results.sort_values('S/N')
        person_results.to_excel(writer, sheet_name='Person Assignments', index=False)
        task_results.to_excel(writer, sheet_name='Task Assignments', index=False)

def print_summary(person_results: pd.DataFrame, task_results: pd.DataFrame):
    """Print a summary of the assignments to the console.
    
    Args:
        person_results (pd.DataFrame): Person-centric results
        task_results (pd.DataFrame): Task-centric results
    """
    print("\nAssignment Summary (by S/N):")
    print("\nFormat: S/N | Name | Role | Number of Assignments | Possible Tasks | Final Assignment")
    print("-" * 100)
    for _, row in person_results.sort_values('S/N').iterrows():
        print(f"S/N {row['S/N']} - {row['Name']} | {row['Role']} | {row['Number of Assignments']}")
        print(f"      Possible Tasks: {row['Possible Tasks']}")
        print(f"      Final Assignment: {row['Final Assignment']}")
        print("-" * 100)
    
    print("\nTask Distribution:")
    print("-" * 100)
    print("Format: Task | Time Slot | Required | Assigned People")
    for _, row in task_results.iterrows():
        print(f"{row['Task']} | {row['Time Slot']} | {row['Required']} | {row['Assigned People']}") 