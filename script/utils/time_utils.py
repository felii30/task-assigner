"""Time-related utility functions."""

from datetime import datetime

def convert_time_format(time_str):
    """Convert time from various formats to HHMM-HHMM format.
    
    Args:
        time_str (str): Time slot string (e.g., "1000-1100" or "3:30 PM-4:30 PM")
        
    Returns:
        str: Standardized time format (e.g., "1000-1100") or None if invalid
    """
    if '-' not in str(time_str):
        return None
    
    try:
        start, end = time_str.split('-')
        # If already in 24-hour format, return as is
        if len(start) == 4 and len(end) == 4:
            return f"{start}-{end}"
        
        # Convert from "HH:MM" format to "HHMM" format
        start_time = datetime.strptime(start.strip(), "%H%M")
        end_time = datetime.strptime(end.strip(), "%H%M")
        return f"{start_time.strftime('%H%M')}-{end_time.strftime('%H%M')}"
    except:
        return None

def check_time_overlap(slot1_start, slot1_end, slot2_start, slot2_end):
    """Check if two time slots overlap.
    
    Args:
        slot1_start (str): Start time of first slot in HHMM format
        slot1_end (str): End time of first slot in HHMM format
        slot2_start (str): Start time of second slot in HHMM format
        slot2_end (str): End time of second slot in HHMM format
        
    Returns:
        bool: True if slots overlap, False otherwise
    """
    return ((slot2_start <= slot1_start and slot2_end > slot1_start) or 
            (slot2_start < slot1_end and slot2_end >= slot1_end) or 
            (slot2_start >= slot1_start and slot2_end <= slot1_end))

def is_fully_available(person, need_start, need_end, availability):
    """Check if a person is available for the entire duration of a time slot.
    
    Args:
        person (int): Person's ID
        need_start (str): Start time in HHMM format
        need_end (str): End time in HHMM format
        availability (dict): Availability data mapping time slots to available people
        
    Returns:
        bool: True if person is available for entire duration, False otherwise
    """
    current_time = need_start
    while current_time < need_end:
        # Find an availability slot that covers this time
        covered = False
        for avail_slot, people in availability.items():
            avail_start, avail_end = avail_slot.split('-')
            if (avail_start <= current_time and avail_end > current_time and 
                person in people):
                covered = True
                current_time = avail_end  # Jump to end of this availability slot
                break
        
        if not covered:
            return False
    
    return True 