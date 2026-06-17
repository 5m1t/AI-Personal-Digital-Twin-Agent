from ..database import DatabaseRepository
from typing import List

db = DatabaseRepository()

def create_study_plan(title: str, topic: str, resources: str = "") -> str:
    """Creates a new learning/study plan for a topic.
    
    Args:
        title: Title of the learning path (e.g. 'Learn Rust Programming').
        topic: Main subject area (e.g., 'Rust', 'Cloud Computing', 'ML').
        resources: Recommended study URLs or book names.
    """
    try:
        plan_id = db.add_learning_plan(title, topic, resources=resources)
        return f"Successfully created study plan ID {plan_id} for '{title}'."
    except Exception as e:
        return f"Error creating study plan: {str(e)}"

def add_quiz_question(plan_id: int, question: str, options: List[str], correct_answer: str) -> str:
    """Adds a quiz question linked to a study plan to test knowledge.
    
    Args:
        plan_id: The ID of the study plan this quiz question belongs to.
        question: The quiz question.
        options: Four choice options as a list of strings.
        correct_answer: The exact correct option text from the options list.
    """
    try:
        if correct_answer not in options:
            return "Error: correct_answer must match one of the options."
        quiz_id = db.add_quiz(plan_id, question, options, correct_answer)
        return f"Successfully added quiz question ID {quiz_id} to plan {plan_id}."
    except Exception as e:
        return f"Error adding quiz question: {str(e)}"

def get_study_plans_summary() -> str:
    """Returns a list of all active study plans and their quizzes."""
    try:
        plans = db.list_learning_plans()
        if not plans:
            return "No active learning plans found."
            
        output = []
        for p in plans:
            quizzes = db.list_quizzes(p['id'])
            output.append(
                f"Study Plan [{p['id']}] {p['title']} (Topic: {p['topic']}) - Status: {p['status']} - Progress: {p['progress']}%\n"
                f"  Resources: {p['resources']}\n"
                f"  Available Quiz Questions: {len(quizzes)}"
            )
            for idx, q in enumerate(quizzes):
                output.append(f"    Q{idx+1}: {q['question']}\n    Choices: {', '.join(q['options'])}")
            output.append("-" * 40)
            
        return "\n".join(output)
    except Exception as e:
        return f"Error gathering study plans: {str(e)}"

def update_study_progress(plan_id: int, progress: int, status: str = "active") -> str:
    """Updates the progress of a study plan.
    
    Args:
        plan_id: Plan ID.
        progress: Completion progress percentage (0-100).
        status: Plan status ('active', 'completed', 'on_hold').
    """
    try:
        db.update_learning_plan(plan_id, {"progress": progress, "status": status})
        return f"Successfully updated learning plan {plan_id} to progress {progress}% and status '{status}'."
    except Exception as e:
        return f"Error updating learning progress: {str(e)}"
