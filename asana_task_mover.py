#!/usr/bin/env python3

import os
import asana
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Asana client
client = asana.Client.access_token(os.getenv('ASANA_TOKEN'))

# Configuration from environment variables
WORKSPACE_ID = os.getenv('WORKSPACE_ID')
TEST_PROJECT_ID = os.getenv('TEST_PROJECT_ID')

def get_incomplete_tasks():
    """Get all incomplete tasks in the test project that are due today or earlier."""
    today = datetime.now().date()
    
    # Get all tasks in the project
    tasks = client.tasks.find_all({
        'project': TEST_PROJECT_ID,
        'completed_since': 'now',  # Only get incomplete tasks
        'due_on': f'<={today.isoformat()}'  # Get tasks due today or earlier
    })
    
    return list(tasks)

def move_task_to_tomorrow(task):
    """Move a task's due date to tomorrow while preserving the time."""
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    # Get the current task details
    task_details = client.tasks.find_by_id(task['gid'])
    
    # If the task has a due time, preserve it
    if task_details.get('due_at'):
        current_time = datetime.fromisoformat(task_details['due_at'].replace('Z', '+00:00'))
        new_due_at = datetime.combine(tomorrow, current_time.time())
        new_due_at = new_due_at.isoformat()
    else:
        new_due_at = tomorrow.isoformat()
    
    # Update the task
    client.tasks.update(task['gid'], {
        'due_on': tomorrow.isoformat(),
        'due_at': new_due_at
    })
    
    # Print the original due date for context
    original_due = task_details.get('due_on', 'No due date')
    print(f"Moved task '{task['name']}' from {original_due} to {tomorrow.isoformat()}")

def main():
    # Validate environment variables
    if not all([os.getenv('ASANA_TOKEN'), os.getenv('WORKSPACE_ID'), os.getenv('TEST_PROJECT_ID')]):
        print("Error: Missing required environment variables.")
        print("Please ensure ASANA_TOKEN, WORKSPACE_ID, and TEST_PROJECT_ID are set in your .env file")
        return

    print("Finding incomplete tasks in test project...")
    tasks = get_incomplete_tasks()
    
    if not tasks:
        print("No incomplete tasks found in the test project.")
        return
    
    print(f"Found {len(tasks)} incomplete tasks. Moving them to tomorrow...")
    
    for task in tasks:
        move_task_to_tomorrow(task)
    
    print("Done!")

if __name__ == "__main__":
    main() 