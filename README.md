# Task Assignment System

A Python-based system for automatically assigning people to tasks based on their availability and task requirements.

## Setup

1. **Python Requirements**

   - Python 3.6 or higher
   - Required packages are listed in `requirements.txt`

2. **Installation**

   ```bash
   # Create and activate a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install required packages from requirements.txt
   pip install -r requirements.txt
   ```

3. **Directory Structure**

   The system uses an event-based directory structure where each event has its own input and output folders:

   ```bash
   .
   ├── README.md
   ├── requirements.txt
   ├── script/
   │   └── main.py
   └── data/
       ├── sample_event/                   # Example event
       │   ├── input/
       │   │   ├── availability.csv
       │   │   └── manpower_needs.csv
       │   └── output/
       └── networking_night/               # Another event
           ├── input/
           └── output/
   ```

## Data Format

### 1. Availability Data (`input/availability.csv`)

Example format:

```csv
,,Role,1530-1630,1630-1730,1730-1830,1830-1930,1930-2030,2030-2130,2130-2230
,,Original Role,Time Slot 1,Time Slot 2,Time Slot 3,Time Slot 4,Time Slot 5,Time Slot 6,Time Slot 7
S/N,Name,Role,,,,,,,
1,John Doe,Setup,1,1,1,0,0,0,0
2,Jane Smith,Usher,0,1,1,1,1,0,0
3,Bob Wilson,AV,0,0,1,1,1,1,0
```

Structure:

- Row 1: Header (can be empty)
- Row 2: Time slots in format "HHMM-HHMM" (e.g., "1530-1800")
- Row 3: Column headers (optional)
- Row 4+: Data rows with:
  - Column 1: S/N (Serial Number)
  - Column 2: Name
  - Column 3: Role
  - Column 4+: Availability markers where:
    - '1' = Available
    - Any other value = Unavailable (will be recorded as reason for unavailability)

### 2. Manpower Needs (`input/manpower_needs.csv`)

Example format:

```csv
Duty Group,Time,Manpower Needed
Setup,1530-1800,8
Catering Ushers,1730-1830,2
Company Ushers,1745-1900,2
AV and Slides,1800-2100,2
Student Registrations,1800-2130,2
Conversation Greasers,1830-2100,8
Photographer,1830-2100,2
Tear Down,2100-2230,8
```

Structure:

- Column 1: Duty Group (task name)
- Column 2: Time slot in HHMM-HHMM format
- Column 3: Number of people needed for this task

## Usage

1. **Create a New Event**

   ```bash
   cd script
   python main.py new_event --init
   ```

   This will:

   - Create the directory structure for your event
   - Copy sample files as templates into the input directory

2. **Prepare Event Data**

   - Navigate to `data/new_event/input/`
   - Edit `availability.csv` with your personnel data
   - Edit `manpower_needs.csv` with your task requirements
   - Make sure all time slots use 24-hour format (HHMM-HHMM)

3. **Run the Assignment**

   ```bash
   cd script
   python main.py new_event
   ```

4. **View Results**
   - Results will be saved in `data/new_event/output/assignments_[timestamp].xlsx`
   - The Excel file contains two sheets:
     - "Person Assignments": Shows each person's possible and assigned tasks
     - "Task Assignments": Shows who is assigned to each task

## Output Format

### Person Assignments Sheet

- S/N: Serial Number
- Name: Person's name
- Role: Original assigned role
- Number of Assignments: How many tasks assigned
- Possible Tasks: All tasks the person could do based on availability
- Final Assignment: Actually assigned task(s)

### Task Assignments Sheet

- Task: Duty group name
- Time Slot: Task timing
- Required: Number of people needed
- Assigned People: List of assigned people with their roles

## Notes

- A person must be available for the ENTIRE duration of a task to be considered for assignment
- The system tries to distribute tasks evenly while meeting all manpower requirements
- Time slots in both files must be in 24-hour format (HHMM-HHMM)
- Each event has its own isolated input and output folders
- Use the `--init` flag when creating a new event to copy template files
