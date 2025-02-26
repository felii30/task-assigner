import pandas as pd
import os
from datetime import datetime

def read_manpower_needs(file_path):
    """Read the manpower needs data and return as a sorted list of requirements."""
    df = pd.read_csv(file_path)
    
    # Convert to list of dictionaries and sort by time
    needs = []
    for _, row in df.iterrows():
        needs.append({
            'duty_group': row['Duty Group'],
            'time_slot': row['Time'],
            'people_needed': row['Manpower Needed']
        })
    
    # Sort by time slot
    needs.sort(key=lambda x: x['time_slot'].split('-')[0])
    return needs

def get_earliest_time(manpower_needs):
    """Get the earliest time from manpower needs."""
    earliest = min(need['time_slot'].split('-')[0] for need in manpower_needs)
    # Convert to 24-hour format if needed
    if len(earliest) == 4:  # Format like "1530"
        return earliest
    else:  # Format like "3:30 PM"
        time_obj = datetime.strptime(earliest, "%I:%M %p")
        return time_obj.strftime("%H%M")

def convert_time_format(time_str):
    """Convert time from '1000-1100' format to '1000-1100' format."""
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

def read_availability_data(file_path, earliest_time):
    """Read availability data and store in a dictionary with time slots as keys."""
    # Read the CSV file
    df = pd.read_csv(file_path, header=None)
    
    # Get the time slots from the second row (index 1)
    time_slots = df.iloc[1, 3:16].tolist()  # Columns 4-16 contain time slots
    
    # Convert time slots to standard format
    time_slots = [convert_time_format(t) for t in time_slots if pd.notna(t)]
    
    # Create availability dictionary
    availability = {}  # Store who's available
    unavailability = {}  # Store who's unavailable and why
    assigned_roles = {}  # Store original assigned roles
    all_people = set()  # Track all people, even if unavailable
    name_mapping = {}  # Map S/N to names
    
    # First, collect all people and their roles
    for idx, row in df.iloc[3:].iterrows():
        if pd.isna(row[0]) or not str(row[0]).strip().isdigit():
            continue
        
        sn = int(row[0])
        # Skip S/N 0
        if sn == 0:
            continue
            
        name = row[1]
        original_role = row[2] if pd.notna(row[2]) else None
        
        # Add to all people set
        all_people.add(sn)
        # Store original role
        assigned_roles[sn] = original_role
        # Store name mapping
        name_mapping[sn] = name
    
    # Process each time slot
    for col_idx, time_slot in enumerate(time_slots, start=3):
        if time_slot:  # Skip if time_slot is None
            # Get start time of slot
            slot_start = time_slot.split('-')[0]
            
            # Create availability and unavailability dictionaries for this slot
            availability[time_slot] = []
            unavailability[time_slot] = {}
            
            # Check availability for each person (start from row 3)
            for idx, row in df.iloc[3:].iterrows():
                if pd.isna(row[0]) or not str(row[0]).strip().isdigit():
                    continue
                
                sn = int(row[0])
                # Skip S/N 0
                if sn == 0:
                    continue
                
                # Check the value in this time slot
                if pd.notna(row[col_idx]):
                    value = str(row[col_idx]).strip()
                    if value == '1':
                        availability[time_slot].append(sn)
                    else:
                        # Store the reason for unavailability
                        unavailability[time_slot][sn] = value
    
    # Now check for overlapping commitments
    for time_slot in availability.keys():
        slot_start, slot_end = time_slot.split('-')
        
        # Remove people who have commitments in overlapping slots
        for check_slot, unavail_dict in unavailability.items():
            check_start, check_end = check_slot.split('-')
            
            # If slots overlap
            if ((check_start <= slot_start and check_end > slot_start) or 
                (check_start < slot_end and check_end >= slot_end) or 
                (check_start >= slot_start and check_end <= slot_end)):
                
                # Remove anyone who has a commitment in the overlapping slot
                availability[time_slot] = [
                    sn for sn in availability[time_slot] 
                    if sn not in unavail_dict
                ]
    
    return availability, assigned_roles, all_people, name_mapping

def assign_tasks(manpower_needs, availability, assigned_roles):
    """Assign tasks based on availability and requirements."""
    assignments = []  # Store all assignments
    assigned_people = {}  # Track how many times each person is assigned
    
    # Process each requirement
    for need in manpower_needs:
        duty_group = need['duty_group']
        time_slot = need['time_slot']
        people_needed = need['people_needed']
        
        # Get available people for this time slot
        need_start, need_end = time_slot.split('-')
        available_people = set()
        
        # First, get all people who are marked as available in any overlapping slot
        potential_people = set()
        for avail_slot, people in availability.items():
            avail_start, avail_end = avail_slot.split('-')
            # Check if slots overlap
            if ((avail_start <= need_start and avail_end > need_start) or 
                (avail_start < need_end and avail_end >= need_end) or 
                (avail_start >= need_start and avail_end <= need_end)):
                potential_people.update(people)
        
        # Then, for each potential person, verify they are available for the ENTIRE duration
        for person in potential_people:
            fully_available = True
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
                    fully_available = False
                    break
            
            if fully_available:
                available_people.add(person)
        
        if not available_people:
            print(f"Warning: No one available for {duty_group} at {time_slot}")
            continue
        
        # Convert to list and sort by number of existing assignments
        available_people = sorted(list(available_people), 
                               key=lambda x: (assigned_people.get(x, 0), x))  # Sort by assignments, then by S/N
        
        # Make assignments
        assigned_to_slot = []
        for person in available_people:
            if len(assigned_to_slot) >= people_needed:
                break
            
            # Add person to assignments
            assigned_to_slot.append(person)
            assigned_people[person] = assigned_people.get(person, 0) + 1
        
        # Record the assignments
        if assigned_to_slot:
            assignments.append({
                'duty_group': duty_group,
                'time_slot': time_slot,
                'required': people_needed,
                'assigned': assigned_to_slot,
                'assigned_with_roles': [f"S/N {p} ({assigned_roles.get(p, '-')})" for p in assigned_to_slot]
            })
    
    return assignments, assigned_people

def format_results(assignments, assigned_people, assigned_roles, all_people, name_mapping, availability):
    """Format results into DataFrames for output."""
    # Person-centric results
    person_results = []
    
    # Process all people, including those with no assignments
    for sn in sorted(all_people):  # Sort by S/N
        # Get all possible assignments (based on availability)
        possible_duties = []
        final_duties = []
        
        for assignment in assignments:
            # Check if person was actually assigned to this task
            if sn in assignment['assigned']:
                final_duties.append(f"{assignment['duty_group']} ({assignment['time_slot']})")
            
            # Check if person could have done this task (must be available for ENTIRE duration)
            need_start, need_end = assignment['time_slot'].split('-')
            
            # Check full duration availability
            fully_available = True
            current_time = need_start
            
            while current_time < need_end:
                # Find an availability slot that covers this time
                covered = False
                for avail_slot, people in availability.items():
                    avail_start, avail_end = avail_slot.split('-')
                    if (avail_start <= current_time and avail_end > current_time and 
                        sn in people):
                        covered = True
                        current_time = avail_end  # Jump to end of this availability slot
                        break
                
                if not covered:
                    fully_available = False
                    break
            
            if fully_available:
                possible_duties.append(f"{assignment['duty_group']} ({assignment['time_slot']})")
        
        person_results.append({
            'S/N': sn,
            'Name': name_mapping[sn],
            'Role': assigned_roles.get(sn, '-'),
            'Number of Assignments': assigned_people.get(sn, 0),
            'Possible Tasks': ', '.join(sorted(set(possible_duties))) if possible_duties else 'No possible tasks',
            'Final Assignment': ', '.join(final_duties) if final_duties else 'No assignments'
        })
    
    # Task-centric results
    task_results = []
    for assignment in assignments:
        # Create a list of assigned people with their names
        assigned_people_with_names = [f"S/N {p} - {name_mapping[p]} ({assigned_roles.get(p, '-')})" 
                                    for p in assignment['assigned']]
        
        task_results.append({
            'Task': assignment['duty_group'],
            'Time Slot': assignment['time_slot'],
            'Required': assignment['required'],
            'Assigned People': ', '.join(assigned_people_with_names)
        })
    
    return pd.DataFrame(person_results), pd.DataFrame(task_results)

def save_results_to_excel(person_results, task_results, output_path):
    """Save results to an Excel file with multiple sheets."""
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sort person_results by S/N before saving
        person_results = person_results.sort_values('S/N')
        person_results.to_excel(writer, sheet_name='Person Assignments', index=False)
        task_results.to_excel(writer, sheet_name='Task Assignments', index=False)

def main():
    # File paths
    availability_path = os.path.join('../data', 'sample_availability_csv.csv')
    manpower_path = os.path.join('../data', 'sample_manpower_needs_csv.csv')
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join('../data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f'task_assignments_{timestamp}.xlsx')
    
    print("\nReading manpower needs...")
    manpower_needs = read_manpower_needs(manpower_path)
    earliest_time = get_earliest_time(manpower_needs)
    
    print(f"\nEarliest required time: {earliest_time}")
    print("\nReading availability data...")
    availability, assigned_roles, all_people, name_mapping = read_availability_data(availability_path, earliest_time)
    
    print("\nMaking assignments...")
    assignments, assigned_people = assign_tasks(manpower_needs, availability, assigned_roles)
    
    # Format and save results
    person_results, task_results = format_results(assignments, assigned_people, assigned_roles, all_people, name_mapping, availability)
    save_results_to_excel(person_results, task_results, output_path)
    
    print(f"\nTask assignments have been saved to: {output_path}")
    
    # Print summary
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

if __name__ == "__main__":
    main()
