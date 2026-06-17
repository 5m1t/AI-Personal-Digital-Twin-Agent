from ..database import DatabaseRepository
from typing import List

db = DatabaseRepository()

def add_career_skill_entry(skill_name: str, proficiency: str = "beginner", certifications: str = "", roadmap: List[str] = None) -> str:
    """Adds or replaces a skill in the user's career portfolio.
    
    Args:
        skill_name: Name of the skill (e.g. 'Python', 'Rust', 'Docker', 'Public Speaking').
        proficiency: Level of proficiency ('beginner', 'intermediate', 'advanced').
        certifications: Certs held or targeted.
        roadmap: Ordered list of milestone steps to acquire/level up this skill.
    """
    try:
        # Check if already exists
        skills = db.list_career_skills()
        exists = any(s['skill_name'].lower() == skill_name.lower() for s in skills)
        if exists:
            db.update_career_skill(skill_name, {"proficiency": proficiency, "certifications": certifications, "roadmap": roadmap or []})
            return f"Updated existing career skill: '{skill_name}' to {proficiency}."
        else:
            skill_id = db.add_career_skill(skill_name, proficiency, certifications, roadmap)
            return f"Successfully recorded new career skill ID {skill_id}: '{skill_name}'."
    except Exception as e:
        return f"Error adding skill: {str(e)}"

def list_career_roadmap_summary() -> str:
    """Returns a structured view of the user's career skills, certifications, and learning roadmaps."""
    try:
        skills = db.list_career_skills()
        if not skills:
            return "No career skills tracked yet."
            
        output = ["### User Career Portfolio & Skills:"]
        for s in skills:
            output.append(
                f"Skill: {s['skill_name']} | Proficiency: {s['proficiency']}\n"
                f"Certifications: {s['certifications'] or 'None'}"
            )
            if s['roadmap']:
                output.append("Roadmap milestones:")
                for idx, step in enumerate(s['roadmap']):
                    output.append(f"  {idx+1}. {step}")
            output.append("-" * 35)
            
        return "\n".join(output)
    except Exception as e:
        return f"Error loading career summary: {str(e)}"
