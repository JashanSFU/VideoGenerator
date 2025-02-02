from moviepy.audio.io.AudioFileClip import AudioFileClip
import praw
import openai
import requests
from moviepy.video.io.VideoFileClip import VideoFileClip
from gtts import gTTS
from pydub import AudioSegment
import os
from openai import OpenAI  # Import new OpenAI client
from secrets_ import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# ====== STEP 1: SCRAPE REDDIT STORY ======
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

def get_top_story(subreddit="AmItheAsshole"):
    try:
        subreddit = reddit.subreddit(subreddit)
        top_post = next(subreddit.top(limit=1))  # Get top story
        return top_post.title + "\n" + top_post.selftext
    except Exception as e:
        print(f"⚠ Error fetching story: {e}")
        return "No story available at the moment."

story = get_top_story()
print("Reddit Story Fetched:\n", story)

# ====== STEP 2: FORMAT STORY USING CHATGPT ======
OPENAI_API_KEY = "your_openai_api_key"
client = OpenAI(api_key=OPENAI_API_KEY)  # Initialize OpenAI Client

def reformat_story(story_text):
    prompt = f"""
    Rewrite this Reddit story to make it engaging, suspenseful, and suitable for narration:
    \n{story_text}\n"""
    
    response = client.chat.completions.create(  # Updated API call
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a professional storyteller."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content  # Updated response handling

formatted_story = reformat_story(story)
print("Formatted Story:\n", formatted_story)

# ====== STEP 3: GENERATE AI VOICEOVER ======
AUDIO_FILE = "voiceover.mp3"

def generate_voiceover(text, output_file=AUDIO_FILE):
    tts = gTTS(text, lang="en")
    tts.save(output_file)

generate_voiceover(formatted_story)

# ====== STEP 4: GET STOCK VIDEO BACKGROUND ======
PEXELS_API_KEY = "your_pexels_api_key"
PEXELS_VIDEO_QUERY = "cinematic background"

def get_stock_video():
    url = f"https://api.pexels.com/videos/search?query={PEXELS_VIDEO_QUERY}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers).json()

    if "videos" not in response or len(response["videos"]) == 0:
        print("⚠ No videos found, using a default video.")
        return "default_background.mp4"  # Use a local fallback video

    video_url = response["videos"][0]["video_files"][0]["link"]
    video_path = "background.mp4"
    
    with open(video_path, "wb") as f:
        f.write(requests.get(video_url).content)
    
    return video_path

video_path = get_stock_video()

# ====== STEP 5: COMBINE VIDEO + AUDIO ======
FINAL_VIDEO = "final_video.mp4"

def create_video(background, audio, output_file=FINAL_VIDEO):
    video_clip = VideoFileClip(background)
    audio_clip = AudioFileClip(audio)

    min_duration = min(video_clip.duration, audio_clip.duration)  # Match lengths
    video_clip = video_clip.subclip(0, min_duration)
    
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_file, fps=24, codec="libx264")

create_video(video_path, AUDIO_FILE)
print("✅ Video Created Successfully: final_video.mp4")


# import praw
# import requests
# import os
# import subprocess
# from gtts import gTTS
# from tqdm import tqdm
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from moviepy.audio.io.AudioFileClip import AudioFileClip
# import moviepy.video as mp
# from secrets_ import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# # ====== STEP 1: FETCH STORY FROM REDDIT ======
# reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
#                      client_secret=REDDIT_CLIENT_SECRET,
#                      user_agent=REDDIT_USER_AGENT)

# def get_top_story(subreddit="AmItheAsshole"):
#     try:
#         subreddit = reddit.subreddit(subreddit)
#         top_post = next(subreddit.top(limit=1))  # Get top story
#         return top_post.title + "\n" + top_post.selftext
#     except Exception as e:
#         print(f"⚠ Error fetching story: {e}")
#         return "No story available at the moment."

# story = get_top_story()
# print("Reddit Story Fetched:\n", story)

# # ====== STEP 2: REWRITE STORY USING OLLAMA AI ======
# def reformat_story_ollama(story_text):
#     story_text = " ".join(story_text.split()[:500])
#     prompt = f"Rewrite this Reddit story to make it engaging, suspenseful, and suitable for narration:\n\n{story_text}"
#     try:
#         result = subprocess.run(
#             ["ollama", "run", "mistral", prompt],
#             capture_output=True,
#             text=True
#         )
#         return result.stdout.strip()
#     except Exception as e:
#         print(f"⚠ Error with Ollama AI: {e}")
#         return story_text

# formatted_story = reformat_story_ollama(story)
# print("Formatted Story:\n", formatted_story)

# # ====== STEP 3: GENERATE AI VOICEOVER ======
# AUDIO_FILE = "voiceover.mp3"

# def generate_voiceover(text, output_file=AUDIO_FILE):
#     print("🔊 Generating voiceover...")
#     text = " ".join(text.split()[:300])
#     tts = gTTS(text, lang="en")
#     tts.save(output_file)
#     print("✅ Voiceover saved as", output_file)

# generate_voiceover(formatted_story)

# # ====== STEP 4: FETCH STOCK VIDEO ======
# PEXELS_VIDEO_QUERY = "cinematic background"

# def get_stock_video():
#     print("📹 Fetching stock video...")
#     url = f"https://api.pexels.com/videos/search?query={PEXELS_VIDEO_QUERY}&per_page=1"
#     headers = {"Authorization": PEXELS_API_KEY}
#     try:
#         response = requests.get(url, headers=headers).json()
#         if "videos" not in response or len(response["videos"]) == 0:
#             print("⚠ No videos found, using a default video.")
#             return "default_background.mp4"
#         video_url = response["videos"][0]["video_files"][0]["link"]
#         video_path = "background.mp4"
#         with open(video_path, "wb") as f:
#             f.write(requests.get(video_url).content)
#         if os.path.getsize(video_path) < 1000:
#             print("⚠ Downloaded video is invalid. Using default video instead.")
#             return "default_background.mp4"
#         print("✅ Stock video saved as", video_path)
#         return video_path
#     except Exception as e:
#         print(f"⚠ Error downloading video: {e}. Using default video.")
#         return "default_background.mp4"

# video_path = get_stock_video()

# # ====== STEP 5: COMBINE VIDEO + AUDIO ======
# FINAL_VIDEO = "final_video.mp4"

# def create_video(background, audio, output_file=FINAL_VIDEO):
#     print("🎬 Combining video and audio...")
#     video_clip = VideoFileClip(background)
#     video_clip = video_clip.resize(height=720)
#     audio_clip = AudioFileClip(audio)
#     min_duration = min(video_clip.duration, audio_clip.duration)
#     video_clip = video_clip.subclip(0, min_duration)
#     video_clip = video_clip.set_audio(audio_clip)
#     with tqdm(total=min_duration, desc="Rendering Video", unit="s") as pbar:
#         def update_progress(current_frame):
#             pbar.update(current_frame / video_clip.fps - pbar.n)
#         video_clip.write_videofile(output_file, fps=24, codec="libx264", threads=4, preset="ultrafast", progress_bar=False, verbose=False, logger=None, callback=update_progress)
#     print("✅ Video Created Successfully:", output_file)

# create_video(video_path, AUDIO_FILE)
