# Asana Task Mover

A Python script to automatically move incomplete Asana tasks to the next day.

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Fill in your values:
     - `ASANA_TOKEN`: Your Asana API token
     - `WORKSPACE_ID`: Your Asana workspace ID
     - `TEST_PROJECT_ID`: Your test project ID
     - `PROJECT_PATH`: Path to this project directory

## Usage

### Using the Desktop Shortcut (Recommended)
The desktop shortcut (`asana-task-mover.desktop`) handles everything automatically:
- Changes to the correct directory
- Sources the `.env` file
- Runs the script

### Manual Usage
If running the script directly, you'll need to:
```bash
# Change to the project directory
cd /path/to/asana-task-mover

# Source the environment variables
source .env

# Run the script
python3 asana_task_mover.py
```

## Security

- API tokens and project IDs are stored in `.env`
- `.env` is git-ignored
- Never commit sensitive data
- Environment variables are automatically handled by the desktop shortcut 