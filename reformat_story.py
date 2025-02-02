import subprocess

def reformat_story_ollama(story_text):
    """
    Rewrite the story using Ollama AI to make it engaging.
    """
    story_text = " ".join(story_text.split()[:500])
    prompt = f"Rewrite this Reddit story to make it engaging, suspenseful, and suitable for narration:\n\n{story_text}"
    
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"⚠ Error with Ollama AI: {e}")
        return story_text


# import os
# import json
# import subprocess

# def reformat_story_ollama(story_text, cache_file="formatted_story.json"):
#     if os.path.exists(cache_file):
#         with open(cache_file, "r") as f:
#             return json.load(f)["formatted_story"]
    
#     story_text = " ".join(story_text.split()[:500])
#     prompt = f"Rewrite this Reddit story to make it engaging, suspenseful, and suitable for narration:\n\n{story_text}"
#     try:
#         result = subprocess.run(
#             ["ollama", "run", "mistral", prompt],
#             capture_output=True,
#             text=True
#         )
#         formatted_story = result.stdout.strip()
#         with open(cache_file, "w") as f:
#             json.dump({"formatted_story": formatted_story}, f)
#         return formatted_story
#     except Exception as e:
#         print(f"⚠ Error with Ollama AI: {e}")
#         return story_text
