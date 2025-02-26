"""Functions for loading and processing input data files."""

import pandas as pd
from typing import List, Tuple

from core.models import Task, AvailabilityData
from utils.time_utils import convert_time_format

def read_manpower_needs(file_path: str) -> List[Task]:
    """Read the manpower needs data and return as a sorted list of tasks.
    
    Args:
        file_path (str): Path to the manpower needs CSV file
        
    Returns:
        List[Task]: List of tasks sorted by start time
    """
    df = pd.read_csv(file_path)
    
    # Convert to list of Task objects and sort by time
    tasks = []
    for _, row in df.iterrows():
        tasks.append(Task(
            duty_group=row['Duty Group'],
            time_slot=row['Time'],
            people_needed=row['Manpower Needed']
        ))
    
    # Sort by time slot
    tasks.sort(key=lambda x: x.time_slot.split('-')[0])
    return tasks

def get_earliest_time(tasks: List[Task]) -> str:
    """Get the earliest time from the list of tasks.
    
    Args:
        tasks (List[Task]): List of tasks
        
    Returns:
        str: Earliest time in HHMM format
    """
    return min(task.time_slot.split('-')[0] for task in tasks)

def read_availability_data(file_path: str) -> AvailabilityData:
    """Read availability data from CSV file.
    
    Args:
        file_path (str): Path to the availability CSV file
        
    Returns:
        AvailabilityData: Container with all availability information
    """
    # Read the CSV file
    df = pd.read_csv(file_path, header=None)
    
    # Get the time slots from the second row (index 1)
    time_slots = df.iloc[1, 3:16].tolist()  # Columns 4-16 contain time slots
    time_slots = [convert_time_format(t) for t in time_slots if pd.notna(t)]
    
    # Initialize data containers
    availability = {}
    assigned_roles = {}
    all_people = set()
    name_mapping = {}
    
    # First, collect all people and their roles
    for _, row in df.iloc[3:].iterrows():
        if pd.isna(row[0]) or not str(row[0]).strip().isdigit():
            continue
        
        sn = int(row[0])
        if sn == 0:  # Skip S/N 0
            continue
            
        name = row[1]
        role = row[2] if pd.notna(row[2]) else None
        
        all_people.add(sn)
        assigned_roles[sn] = role
        name_mapping[sn] = name
    
    # Process each time slot
    for col_idx, time_slot in enumerate(time_slots, start=3):
        if time_slot:  # Skip if time_slot is None
            availability[time_slot] = []
            
            # Check availability for each person
            for _, row in df.iloc[3:].iterrows():
                if pd.isna(row[0]) or not str(row[0]).strip().isdigit():
                    continue
                
                sn = int(row[0])
                if sn == 0:  # Skip S/N 0
                    continue
                
                # Check the value in this time slot
                if pd.notna(row[col_idx]) and str(row[col_idx]).strip() == '1':
                    availability[time_slot].append(sn)
    
    return AvailabilityData(
        availability=availability,
        assigned_roles=assigned_roles,
        all_people=all_people,
        name_mapping=name_mapping
    ) 