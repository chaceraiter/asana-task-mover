#!/usr/bin/env python3

import os
import asana
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Asana client
client = asana.Client.access_token(os.getenv('ASANA_TOKEN'))

# Configuration from environment variables
WORKSPACE_ID = os.getenv('WORKSPACE_ID')
TEST_PROJECT_ID = os.getenv('TEST_PROJECT_ID')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'test').lower()  # Default to 'test' if not set

def convert_to_local_date(date_str):
    """Convert an ISO date string to local date."""
    print(f"Converting date: {date_str}")
    # Parse the date in UTC
    utc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    print(f"Parsed UTC date: {utc_date}")
    # Convert to local time
    local_date = utc_date.astimezone()
    print(f"Converted to local date: {local_date.date()}")
    return local_date.date()

def get_incomplete_tasks():
    """Get incomplete tasks based on the current environment."""
    print("Finding incomplete tasks...")
    print(f"\nCurrent local date: {datetime.now().date()}")
    
    # Set up the query parameters based on environment
    if ENVIRONMENT == 'test':
        print("Running in test mode - only processing tasks from test project")
        query_params = {
            'project': TEST_PROJECT_ID,
            'completed_since': 'now',
            'opt_fields': 'name,due_on,due_at'
        }
    else:
        print("Running in production mode - processing all tasks in workspace")
        query_params = {
            'workspace': WORKSPACE_ID,
            'assignee': 'me',
            'completed_since': 'now',
            'opt_fields': 'name,due_on,due_at'
        }
    
    # Debug print to show the query parameters
    print("Debug: Query parameters being sent to Asana:", query_params)
    
    # Get tasks based on the environment
    tasks = client.tasks.find_all(query_params)
    
    tasks_to_move = []
    today = datetime.now().date()
    
    for task in tasks:
        print("\n" + "="*50)
        print(f"Task: {task['name']}")
        print("  Current state:")
        
        # Check if task has a time component
        has_time = task.get('due_at') is not None
        
        if has_time:
            # For tasks with time, use due_at for comparison
            due_at = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00'))
            task_date = due_at.date()
            print(f"    Due at (UTC): {task['due_at']}")
        elif task.get('due_on'):
            # For tasks with just a date, use due_on
            task_date = datetime.fromisoformat(task['due_on']).date()
            print(f"    Due on (UTC): {task['due_on']}")
        else:
            # Skip tasks with no due date
            print("    No due date")
            continue
        
        print(f"    Has time: {has_time}")
        print("  Comparison:")
        print(f"    Task date: {task_date}")
        print(f"    Today's date: {today}")
        
        # Check if the task is due today or tomorrow but before local midnight
        if task_date <= today or (task_date == today + timedelta(days=1) and has_time and due_at.time() < datetime.now().time()):
            print("  -> Will be moved (due today or tomorrow before local midnight)")
            tasks_to_move.append(task)
        else:
            print("  -> Will be skipped (due after tomorrow or after local midnight)")
    
    print(f"\nFound {len(tasks_to_move)} incomplete tasks. Moving them to tomorrow...")
    return tasks_to_move

def move_task_to_tomorrow(task):
    """Move a task to tomorrow while preserving its time component if it has one."""
    print("\n" + "="*50)
    print(f"Moving task: {task['name']}")
    print("  Current state:")
    print(f"    Due on: {task.get('due_on')}")
    print(f"    Due at: {task.get('due_at')}")
    
    # Check if task has a time component
    has_time = task.get('due_at') is not None
    
    if has_time:
        print("  Task has time component")
        # Parse the UTC time from due_at
        due_at = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00'))
        print(f"  Original UTC time: {due_at}")
        
        # Create new datetime with tomorrow's date but same time
        tomorrow = datetime.now().date() + timedelta(days=1)
        new_due_at = datetime.combine(tomorrow, due_at.time(), tzinfo=timezone.utc)
        print(f"  New UTC datetime: {new_due_at}")
        
        # Convert to local time to check if it's still today
        local_new_due_at = new_due_at.astimezone()
        print(f"  New local datetime: {local_new_due_at}")
        
        # If the new due time in local time is still today, add one more day
        if local_new_due_at.date() <= datetime.now().date():
            print("  New due time is still today in local time. Adding one more day.")
            new_due_at = new_due_at + timedelta(days=1)
            print(f"  Adjusted UTC datetime: {new_due_at}")
        
        # Format for Asana API
        new_due_at_str = new_due_at.isoformat()
        print(f"  Final UTC time for Asana: {new_due_at_str}")
        
        # Update the task with new due_at
        client.tasks.update(task['gid'], {'due_at': new_due_at_str})
        
        # Verify the update
        updated_task = client.tasks.find_by_id(task['gid'], opt_fields=['due_at'])
        print("  Updated state:")
        print(f"    Due at: {updated_task['due_at']}")
        print(f"  Summary: Moved from {task['due_on']} to {new_due_at.date()}")
    else:
        print("  Task has date only")
        # For tasks without time, just update due_on
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        print(f"  Setting due_on to: {tomorrow}")
        
        client.tasks.update(task['gid'], {'due_on': tomorrow})
        
        # Verify the update
        updated_task = client.tasks.find_by_id(task['gid'], opt_fields=['due_on'])
        print("  Updated state:")
        print(f"    Due on: {updated_task['due_on']}")
        print(f"  Summary: Moved from {task['due_on']} to {tomorrow}")

def main():
    # Validate environment variables
    if not all([os.getenv('ASANA_TOKEN'), os.getenv('WORKSPACE_ID'), os.getenv('TEST_PROJECT_ID')]):
        print("Error: Missing required environment variables.")
        print("Please ensure ASANA_TOKEN, WORKSPACE_ID, and TEST_PROJECT_ID are set in your .env file")
        return

    print(f"Running in {ENVIRONMENT} environment...")
    print("Finding incomplete tasks...")
    tasks = get_incomplete_tasks()
    
    if not tasks:
        print("No incomplete tasks found.")
        return
    
    print(f"\nFound {len(tasks)} incomplete tasks. Moving them to tomorrow...")
    
    for task in tasks:
        move_task_to_tomorrow(task)
    
    print("\nDone!")

if __name__ == "__main__":
    main() 