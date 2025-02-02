import os
from fetch_story import get_top_story
from reformat_story import reformat_story_ollama
from generate_voiceover import generate_voiceover
from fetch_video import get_stock_video
from create_video import create_video

# Define cache paths
CACHE_DIR = "cache"
RESULTS_DIR = "results"

STORY_FILE = os.path.join(CACHE_DIR, "story.txt")
FORMATTED_FILE = os.path.join(CACHE_DIR, "formatted_story.txt")
VOICEOVER_FILE = os.path.join(RESULTS_DIR, "voiceover.mp3")
VIDEO_FILE = os.path.join(RESULTS_DIR, "background.mp4")
FINAL_VIDEO = os.path.join(RESULTS_DIR, "final_video.mp4")

def ensure_dir(directory):
    """ Ensure that a directory exists """
    if not os.path.exists(directory):
        os.makedirs(directory)

def read_cache(file_path):
    """ Read a file from cache if it exists """
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def write_cache(file_path, data):
    """ Write data to a cache file, ensuring directory exists """
    ensure_dir(CACHE_DIR)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data)

# Ensure directories exist
ensure_dir(CACHE_DIR)
ensure_dir(RESULTS_DIR)

# Step 1: Fetch story
story = read_cache(STORY_FILE)
if not story:
    print("📜 Fetching new story...")
    story = get_top_story()
    write_cache(STORY_FILE, story)
else:
    print("🔄 Using cached story...")

# Step 2: Format story
formatted_story = read_cache(FORMATTED_FILE)
if not formatted_story:
    print("✍ Formatting story...")
    formatted_story = reformat_story_ollama(story)
    write_cache(FORMATTED_FILE, formatted_story)
else:
    print("🔄 Using cached formatted story...")

# Step 3: Generate voiceover
if not os.path.exists(VOICEOVER_FILE):
    print("🔊 Generating new voiceover...")
    generate_voiceover(formatted_story, VOICEOVER_FILE)
else:
    print("🔊 Using cached voiceover...")

# Step 4: Fetch stock video
if not os.path.exists(VIDEO_FILE) or os.path.getsize(VIDEO_FILE) < 1000:
    print("🎥 Fetching new stock video...")
    video_path = get_stock_video()
    os.rename(video_path, VIDEO_FILE)
else:
    print("📹 Using cached stock video...")
    video_path = VIDEO_FILE

# Step 5: Create final video
print("🎬 Creating final video...")
create_video(video_path, VOICEOVER_FILE, FINAL_VIDEO, title="Reddit Story", story_text=formatted_story)

print("✅ Video creation complete:", FINAL_VIDEO)
