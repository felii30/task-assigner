"""Data models for task assignment system."""

from dataclasses import dataclass
from typing import List, Dict, Set

@dataclass
class Task:
    """Represents a task that needs to be assigned."""
    duty_group: str
    time_slot: str
    people_needed: int

@dataclass
class Assignment:
    """Represents a task assignment with assigned people."""
    duty_group: str
    time_slot: str
    required: int
    assigned: List[int]
    assigned_with_roles: List[str]

@dataclass
class PersonInfo:
    """Represents information about a person."""
    sn: int
    name: str
    role: str
    assignments_count: int
    possible_tasks: List[str]
    final_assignments: List[str]

@dataclass
class AvailabilityData:
    """Container for all availability-related data."""
    availability: Dict[str, List[int]]  # time_slot -> list of available people
    assigned_roles: Dict[int, str]      # person_id -> original role
    all_people: Set[int]                # set of all person IDs
    name_mapping: Dict[int, str]        # person_id -> name 