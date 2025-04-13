import os

def save_draft(topic):
    filename = f"blog/{topic.replace(' ', '_')}.md"
    os.makedirs("blog", exist_ok=True)
    content = f"# {topic.title()}\n\nExploring {topic} in 2025.\n\nBy Hyperballoid"
    with open(filename, "w") as f:
        f.write(content)
