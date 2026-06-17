from ..database import DatabaseRepository
import datetime
from typing import List

db = DatabaseRepository()

def log_daily_wellness(sleep_hours: float, exercise_minutes: int, calories_burned: int = 0, mood: str = "good", habits_checked: List[str] = None) -> str:
    """Logs daily health and wellness statistics for the user (sleep, exercise, mood, habits).
    
    Args:
        sleep_hours: Hours of sleep last night (e.g. 7.5).
        exercise_minutes: Exercise duration in minutes today.
        calories_burned: Calories burned today.
        mood: Qualitative mood state (e.g., 'rested', 'energetic', 'tired', 'stressed').
        habits_checked: List of habits completed today (e.g., ['Drink 3L Water', 'No screens in bed']).
    """
    try:
        today_str = datetime.date.today().isoformat()
        db.log_wellness(today_str, sleep_hours, exercise_minutes, calories_burned, mood, habits_checked)
        return f"Successfully logged wellness stats for today ({today_str}): Sleep: {sleep_hours}h, Exercise: {exercise_minutes}m, Mood: {mood}."
    except Exception as e:
        return f"Error logging wellness stats: {str(e)}"

def get_wellness_report() -> str:
    """Generates a summary of recent wellness metrics and trends (e.g., average sleep, exercise)."""
    try:
        logs = db.list_wellness_logs(limit=7)
        if not logs:
            return "No recent wellness logs found."
            
        output = []
        output.append("### Wellness Report (Last 7 Days):")
        total_sleep = 0
        total_exercise = 0
        days = len(logs)
        
        for log in logs:
            total_sleep += log['sleep_hours'] or 0
            total_exercise += log['exercise_minutes'] or 0
            output.append(
                f"- Date: {log['date']} | Sleep: {log['sleep_hours']}h | Exercise: {log['exercise_minutes']}m | Mood: {log['mood']} | Habits: {', '.join(log['habits'] or [])}"
            )
            
        avg_sleep = total_sleep / days if days > 0 else 0
        avg_exercise = total_exercise / days if days > 0 else 0
        output.append(f"\nAverage Sleep: {avg_sleep:.1f} hours/day")
        output.append(f"Average Exercise: {avg_exercise:.1f} minutes/day")
        
        # Wellness advice
        if avg_sleep < 7.0:
            output.append("💡 Recommendation: Sleep average is below 7 hours. Try starting a wind-down routine 30 minutes earlier.")
        if avg_exercise < 30:
            output.append("💡 Recommendation: Exercise is below the recommended 30 minutes daily. Let's block out 20 mins tomorrow morning for a walk.")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error loading wellness report: {str(e)}"
