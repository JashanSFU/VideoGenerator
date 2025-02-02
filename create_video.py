import subprocess
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.fx.loop import loop
from moviepy.editor import TextClip, CompositeVideoClip
from tqdm import tqdm
import re
import textwrap

def split_text_into_phrases(text, duration, min_words=4, max_words=10):
    """
    Splits text into natural phrases without cutting words.
    - Ensures each phrase lasts long enough to be read.
    - Uses punctuation (.,!?) for better readability.
    """
    words = text.split()
    phrases = []
    temp_phrase = []

    for word in words:
        temp_phrase.append(word)
        if len(temp_phrase) >= min_words and re.search(r"[.!?]", word):
            phrases.append(" ".join(temp_phrase))
            temp_phrase = []

    # If there are remaining words, add them as the last phrase
    if temp_phrase:
        phrases.append(" ".join(temp_phrase))

    num_phrases = len(phrases)
    interval = duration / num_phrases if num_phrases > 0 else 3  # Default interval

    subtitle_timestamps = []
    offset_position = 0  # To alternate subtitle positions

    for i, phrase in enumerate(phrases):
        start_time = i * interval
        offset_position = (offset_position + 1) % 2  # Alternating position
        subtitle_timestamps.append((start_time, phrase, offset_position))

    return subtitle_timestamps

RESULTS_DIR = "results"

def ensure_dir(directory):
    """ Ensure that a directory exists """
    if not os.path.exists(directory):
        os.makedirs(directory)

def resize_video(input_file, output_file=None, height=720):
    """ Resizes a video using FFmpeg, ensuring width is even. """
    ensure_dir(RESULTS_DIR)

    if output_file is None:
        output_file = os.path.join(RESULTS_DIR, "resized_background.mp4")

    print("📏 Resizing video using FFmpeg...")

    if not os.path.exists(input_file) or os.path.getsize(input_file) < 1000:
        print("❌ Input video file is missing or too small. Skipping resize.")
        return input_file

    command = [
        "ffmpeg", "-y", "-i", input_file,
        "-vf", f"scale=trunc(iw/2)*2:{height}",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "192k",
        output_file
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
        print(f"✅ Resized video saved as {output_file}")
        return output_file
    else:
        print(f"⚠ Resizing failed: {process.stderr.decode()}")
        return input_file

def create_video(background, audio, output_file=None, title="Reddit Story", story_text=""):
    """ Combines resized video with AI-generated voiceover and adds properly timed subtitles. """
    ensure_dir(RESULTS_DIR)

    if output_file is None:
        output_file = os.path.join(RESULTS_DIR, "final_video.mp4")

    print("🎬 Combining video and audio...")

    if not story_text:
        print("⚠ No captions provided!")

    # Resize video first
    background_resized = resize_video(background)

    try:
        video_clip = VideoFileClip(background_resized)
        audio_clip = AudioFileClip(audio)

        if video_clip.w == 0 or video_clip.h == 0:
            raise ValueError("❌ Error: Video width or height is 0.")

        if video_clip.duration == 0 or audio_clip.duration == 0:
            raise ValueError("❌ Error: Invalid video or audio file.")

        # Ensure video matches audio duration
        if video_clip.duration < audio_clip.duration:
            print("🔄 Looping video to match voiceover duration...")
            video_clip = loop(video_clip, duration=audio_clip.duration)
        else:
            video_clip = video_clip.subclip(0, audio_clip.duration)

        video_clip = video_clip.set_audio(audio_clip)

        # Generate subtitles
        subtitles = split_text_into_phrases(story_text, audio_clip.duration)

        # ** Title (Appears at top) **
        title_clip = TextClip(
            title,
            fontsize=55,
            color="white",
            font="Arial-Bold",
            stroke_color="black",
            stroke_width=3,
            method="label",
            size=(video_clip.w - 200, None)
        ).set_position(("center", 50)).set_duration(audio_clip.duration)

        # ** Subtitles (Alternate Positions to Avoid Overlap) **
        subtitle_clips = [title_clip]

        for timestamp, text, position in subtitles:
            y_offset = video_clip.h - 250 if position == 0 else video_clip.h - 300

            subtitle_text = TextClip(
                text,
                fontsize=45,
                color='yellow',  # Highlight spoken words
                font="Arial-Bold",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(video_clip.w - 200, None)  
            ).set_position(("center", y_offset)).set_start(timestamp).set_duration(4)

            subtitle_clips.append(subtitle_text)

        final_video = CompositeVideoClip([video_clip] + subtitle_clips)

        with tqdm(total=int(audio_clip.duration), desc="Rendering Video", unit="s") as pbar:
            def update_progress(current_frame):
                pbar.update(current_frame / final_video.fps - pbar.n)

            final_video.write_videofile(output_file, fps=24, codec="libx264", threads=4, preset="ultrafast")

        video_clip.reader.close()
        video_clip.audio.reader.close()

        print("✅ Video Created Successfully:", output_file)

    except Exception as e:
        print(f"❌ Error creating video: {e}")
