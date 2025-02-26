"""Main script for task assignment system."""

import os
from datetime import datetime

from utils.data_loader import read_manpower_needs, read_availability_data
from core.assigner import assign_tasks
from utils.output_formatter import format_results, save_results_to_excel, print_summary

def main():
    """Main function to run the task assignment system."""
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
    tasks = read_manpower_needs(manpower_path)
    
    print("\nReading availability data...")
    availability_data = read_availability_data(availability_path)
    
    print("\nMaking assignments...")
    assignments, assigned_people = assign_tasks(tasks, availability_data)
    
    # Format and save results
    person_results, task_results = format_results(
        assignments=assignments,
        assigned_people=assigned_people,
        availability_data=availability_data
    )
    
    save_results_to_excel(person_results, task_results, output_path)
    print(f"\nTask assignments have been saved to: {output_path}")
    
    print_summary(person_results, task_results)

if __name__ == "__main__":
    main()
