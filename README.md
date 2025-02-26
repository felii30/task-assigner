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

3. **Data Folder Setup**

   ```bash
   # Create the required directory structure
   mkdir -p data/output

   # Your directory structure should look like this:
   # .
   # ├── README.md
   # ├── requirements.txt
   # ├── script/
   # │   └── main.py
   # └── data/
   #     ├── sample_availability_csv.csv
   #     ├── sample_manpower_needs_csv.csv
   #     └── output/
   ```

## Data Format

### 1. Availability Data (`data/sample_availability_csv.csv`)

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

### 2. Manpower Needs (`data/sample_manpower_needs_csv.csv`)

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

1. **Prepare Data Files**

   - Create your availability data following the format above and save as `data/sample_availability_csv.csv`
   - Create your manpower needs following the format above and save as `data/sample_manpower_needs_csv.csv`
   - Make sure all time slots use 24-hour format (HHMM-HHMM)

2. **Run the Script**

   ```bash
   cd script
   python main.py
   ```

3. **View Results**
   - Results will be saved in `data/output/task_assignments_[timestamp].xlsx`
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
- The output directory (`data/output/`) is automatically created if it doesn't exist
