"""Main script for task assignment system."""

import os
from datetime import datetime
import argparse

from utils.data_loader import read_manpower_needs, read_availability_data
from core.assigner import assign_tasks
from utils.output_formatter import format_results, save_results_to_excel, print_summary

def setup_event_directories(event_name: str) -> tuple[str, str, str]:
    """Set up directories for a specific event.
    
    Args:
        event_name (str): Name of the event (e.g., 'sample_event')
        
    Returns:
        tuple[str, str, str]: Paths to event directory, input directory, and output directory
    """
    # Create event directory structure
    event_dir = os.path.join('../data', event_name)
    input_dir = os.path.join(event_dir, 'input')
    output_dir = os.path.join(event_dir, 'output')
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    return event_dir, input_dir, output_dir

def copy_sample_files(input_dir: str):
    """Copy sample files to the input directory if it's empty.
    
    Args:
        input_dir (str): Path to input directory
    """
    if not os.listdir(input_dir):
        import shutil
        # Use the sample CSV files from data root as templates
        for src_file, dst_file in [
            ('sample_availability_csv.csv', 'availability.csv'),
            ('sample_manpower_needs_csv.csv', 'manpower_needs.csv')
        ]:
            src = os.path.join('../data', src_file)
            dst = os.path.join(input_dir, dst_file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"Copied sample file: {src_file} -> {dst_file}")

def main():
    """Main function to run the task assignment system."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Task Assignment System')
    parser.add_argument('event_name', help='Name of the event (e.g., sample_event)')
    parser.add_argument('--init', action='store_true', 
                       help='Initialize event with sample files if input directory is empty')
    args = parser.parse_args()
    
    # Set up event directories
    event_dir, input_dir, output_dir = setup_event_directories(args.event_name)
    
    # Copy sample files if requested and input directory is empty
    if args.init:
        copy_sample_files(input_dir)
    
    # File paths
    availability_path = os.path.join(input_dir, 'availability.csv')
    manpower_path = os.path.join(input_dir, 'manpower_needs.csv')
    
    # Check if input files exist
    if not os.path.exists(availability_path) or not os.path.exists(manpower_path):
        print(f"\nError: Required input files not found in {input_dir}")
        print("Expected files:")
        print(f"  - {availability_path}")
        print(f"  - {manpower_path}")
        print("\nYou can:")
        print("1. Copy your input files to the above locations, or")
        print(f"2. Run with --init to copy sample files: python main.py {args.event_name} --init")
        return
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f'assignments_{timestamp}.xlsx')
    
    print(f"\nProcessing event: {args.event_name}")
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
