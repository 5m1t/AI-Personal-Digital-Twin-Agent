from ..database import DatabaseRepository
import json

db = DatabaseRepository()

def create_new_goal(title: str, description: str = "", category: str = "personal", target_date: str = "") -> str:
    """Creates a new long-term goal for the user.
    
    Args:
        title: The name/title of the goal (e.g. 'Complete AWS Certified Developer certification').
        description: Details or steps about the goal.
        category: Category of goal ('career', 'learning', 'wellness', 'finance', 'personal').
        target_date: Target completion date in YYYY-MM-DD format.
    """
    try:
        goal_id = db.add_goal(title, description, category, target_date)
        return f"Successfully created goal ID {goal_id}: '{title}'."
    except Exception as e:
        return f"Error creating goal: {str(e)}"

def add_task_to_goal(goal_id: int, title: str, description: str = "", due_date: str = "", priority: str = "medium") -> str:
    """Adds a task or milestone linked to a specific goal.
    
    Args:
        goal_id: The ID of the goal this task is associated with.
        title: Task name (e.g., 'Read Chapter 4 of AWS book').
        description: Detail descriptions.
        due_date: Due date in YYYY-MM-DD.
        priority: Task priority ('low', 'medium', 'high').
    """
    try:
        task_id = db.add_task(title, description, goal_id, due_date, priority)
        return f"Successfully created task ID {task_id} under goal {goal_id}."
    except Exception as e:
        return f"Error adding task: {str(e)}"

def get_goals_and_tasks_summary() -> str:
    """Returns a formatted summary of all current goals, progress, and task statuses."""
    try:
        goals = db.list_goals()
        if not goals:
            return "No goals tracked yet."
        
        output = []
        for g in goals:
            tasks = db.list_tasks(g['id'])
            todo = sum(1 for t in tasks if t['status'] == 'todo')
            progress_t = sum(1 for t in tasks if t['status'] == 'in_progress')
            done = sum(1 for t in tasks if t['status'] == 'done')
            
            output.append(
                f"Goal [{g['id']}] {g['title']} ({g['category']}) - Status: {g['status']} - Progress: {g['progress']}%\n"
                f"  Description: {g['description']}\n"
                f"  Target Date: {g['target_date']}\n"
                f"  Tasks: {todo} Todo | {progress_t} In Progress | {done} Done"
            )
            for t in tasks:
                output.append(f"    - Task [{t['id']}] {t['title']} (Priority: {t['priority']}, Status: {t['status']}, Due: {t['due_date']})")
            output.append("-" * 40)
            
        return "\n".join(output)
    except Exception as e:
        return f"Error loading summary: {str(e)}"

def update_task_state(task_id: int, status: str) -> str:
    """Updates the status of a specific task.
    
    Args:
        task_id: The ID of the task.
        status: The new status ('todo', 'in_progress', 'done').
    """
    try:
        if status not in ('todo', 'in_progress', 'done'):
            return "Invalid status. Use 'todo', 'in_progress', or 'done'."
        db.update_task(task_id, {"status": status})
        return f"Successfully updated task {task_id} status to '{status}'."
    except Exception as e:
        return f"Error updating task: {str(e)}"

def update_goal_state(goal_id: int, progress: int, status: str = "in_progress") -> str:
    """Updates the progress percentage and status of a goal.
    
    Args:
        goal_id: Goal ID.
        progress: Completion percentage (0 to 100).
        status: Goal status ('in_progress', 'completed', 'cancelled').
    """
    try:
        db.update_goal(goal_id, {"progress": progress, "status": status})
        return f"Successfully updated goal {goal_id} to progress {progress}% and status '{status}'."
    except Exception as e:
        return f"Error updating goal: {str(e)}"

def analyze_productivity_bottlenecks() -> str:
    """Analyzes tasks and flags goals with overdue tasks or high count of unfinished tasks."""
    try:
        tasks = db.list_tasks()
        goals = db.list_goals()
        
        overdue_tasks = []
        import datetime
        today_str = datetime.date.today().isoformat()
        
        for t in tasks:
            if t['status'] != 'done' and t['due_date'] and t['due_date'] < today_str:
                overdue_tasks.append(t)
                
        output = []
        if overdue_tasks:
            output.append("### Overdue Tasks Detected:")
            for t in overdue_tasks:
                output.append(f"- Task [{t['id']}] '{t['title']}' was due on {t['due_date']} (Priority: {t['priority']})")
        else:
            output.append("No overdue tasks found.")
            
        # Analyze goal progress bottleneck
        for g in goals:
            g_tasks = db.list_tasks(g['id'])
            pending = sum(1 for t in g_tasks if t['status'] != 'done')
            if pending > 4 and g['progress'] < 50:
                output.append(f"\n### Goal Bottleneck Warning:\nGoal [{g['id']}] '{g['title']}' has {pending} uncompleted tasks and is under 50% progress.")
                
        return "\n".join(output)
    except Exception as e:
        return f"Error analyzing productivity: {str(e)}"
