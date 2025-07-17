import random

TEMPLATES = [
    {
        "name": "Productivity",
        "notes": [
            ("meeting_notes", "Discussed Q3 goals and project timelines."),
            ("todo_list", "1. Finalize report\n2. Email team about updates\n3. Schedule follow-up meeting"),
            ("brainstorming", "Ideas for new marketing campaign: social media contest, influencer outreach, email newsletter."),
        ],
        "tags": ["#work", "#productivity", "#goals"]
    },
    {
        "name": "Minimalist",
        "notes": [
            ("daily_reflection", "Today was a quiet day. I enjoyed the simplicity of my routine."),
            ("gratitude_journal", "I'm grateful for the warm cup of coffee this morning and the beautiful sunset."),
            ("favorite_quote", "“The secret of happiness, you see, is not found in seeking more, but in developing the capacity to enjoy less.” - Socrates"),
        ],
        "tags": ["#minimalism", "#simplicity", "#gratitude"]
    },
    {
        "name": "Creative",
        "notes": [
            ("poem_idea", "A poem about a forgotten path in a forest."),
            ("doodle_description", "A sketch of a cat wearing a tiny hat."),
            ("story_prompt", "A character who can talk to ghosts, but only on Tuesdays."),
        ],
        "tags": ["#creative", "#writing", "#art"]
    }
]

def get_random_template():
    return random.choice(TEMPLATES)
