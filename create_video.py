# import subprocess
# import os
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from moviepy.audio.io.AudioFileClip import AudioFileClip
# from moviepy.video.fx.loop import loop
# from tqdm import tqdm

# RESULTS_DIR = "results"

# def ensure_dir(directory):
#     """ Ensure that a directory exists """
#     if not os.path.exists(directory):
#         os.makedirs(directory)

# def resize_video(input_file, output_file=None, height=720):
#     """
#     Resizes a video to a specific height using FFmpeg, ensuring the width is even.
#     """
#     ensure_dir(RESULTS_DIR)

#     if output_file is None:
#         output_file = os.path.join(RESULTS_DIR, "resized_background.mp4")

#     print("📏 Resizing video using FFmpeg...")

#     if not os.path.exists(input_file) or os.path.getsize(input_file) < 1000:
#         print("❌ Input video file is missing or too small. Skipping resize.")
#         return input_file

#     command = [
#         "ffmpeg", "-y", "-i", input_file,
#         "-vf", f"scale=trunc(iw/2)*2:{height}",  # Ensure width is even
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-c:a", "aac", "-b:a", "192k",
#         output_file
#     ]

#     process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
#         print(f"✅ Resized video saved as {output_file}")
#         return output_file
#     else:
#         print(f"⚠ Resizing failed: {process.stderr.decode()}")
#         return input_file

# def create_video(background, audio, output_file=None):
#     """
#     Combines resized video with AI-generated voiceover and loops the video if needed.
#     """
#     ensure_dir(RESULTS_DIR)

#     if output_file is None:
#         output_file = os.path.join(RESULTS_DIR, "final_video.mp4")

#     print("🎬 Combining video and audio...")

#     # Resize video first
#     background_resized = resize_video(background)

#     try:
#         video_clip = VideoFileClip(background_resized, target_resolution=(720, 1280))  # Adjust to match aspect ratio
#         audio_clip = AudioFileClip(audio)

#         # Ensure valid files
#         if video_clip.duration == 0 or audio_clip.duration == 0:
#             raise ValueError("Invalid video or audio file, cannot process.")

#         # Adjust video duration to match voiceover
#         if video_clip.duration < audio_clip.duration:
#             print("🔄 Looping video to match voiceover duration...")
#             video_clip = loop(video_clip, duration=audio_clip.duration)
#         else:
#             video_clip = video_clip.subclip(0, audio_clip.duration)

#         video_clip = video_clip.set_audio(audio_clip)

#         with tqdm(total=int(audio_clip.duration), desc="Rendering Video", unit="s") as pbar:
#             def update_progress(current_frame):
#                 pbar.update(current_frame / video_clip.fps - pbar.n)

#             video_clip.write_videofile(
#                 output_file, fps=24, codec="libx264", threads=4, preset="ultrafast"
#             )
#         video_clip.reader.close()  # Ensure proper cleanup
#         video_clip.audio.reader.close()

#         print("✅ Video Created Successfully:", output_file)

#     except Exception as e:
#         print(f"❌ Error creating video: {e}")


import subprocess
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.fx.loop import loop
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
from tqdm import tqdm

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
        return input_file  # Return original video if resize fails

    command = [
        "ffmpeg", "-y", "-i", input_file,
        "-vf", f"scale=trunc(iw/2)*2:{height}",  # Ensure width is even
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "192k",
        output_file
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
        print(f"✅ Resized video saved as {output_file}")
        return output_file
    else:
        print(f"⚠ Resizing failed: {process.stderr.decode()} - Using original video instead.")
        return input_file  # Return original video if resize fails

def split_text_into_chunks(text, duration, num_chunks=20):
    """
    Splits text into small chunks evenly distributed across duration.
    """
    import textwrap
    words = text.split()
    chunk_size = max(1, len(words) // num_chunks)  # Avoid division by zero
    chunks = textwrap.wrap(text, width=chunk_size)

    subtitle_timestamps = []
    interval = duration / len(chunks) if chunks else 3  # Default interval = 3s
    for i, chunk in enumerate(chunks):
        start_time = i * interval
        subtitle_timestamps.append((start_time, chunk))

    return subtitle_timestamps

def create_video(background, audio, output_file=None, title="Reddit Story", story_text=""):
    """ Combines resized video with AI-generated voiceover and adds perfectly timed subtitles. """
    ensure_dir(RESULTS_DIR)

    if output_file is None:
        output_file = os.path.join(RESULTS_DIR, "final_video.mp4")

    print("🎬 Combining video and audio...")

    # Resize video first
    background_resized = resize_video(background)

    try:
        video_clip = VideoFileClip(background_resized)
        audio_clip = AudioFileClip(audio)

        if video_clip.w == 0 or video_clip.h == 0:
            raise ValueError("Invalid video dimensions (width or height is 0).")

        if video_clip.duration == 0 or audio_clip.duration == 0:
            raise ValueError("Invalid video or audio file, cannot process.")

        # Adjust video duration to match voiceover
        if video_clip.duration < audio_clip.duration:
            print("🔄 Looping video to match voiceover duration...")
            video_clip = loop(video_clip, duration=audio_clip.duration)
        else:
            video_clip = video_clip.subclip(0, audio_clip.duration)

        video_clip = video_clip.set_audio(audio_clip)

        # Split the story into timed captions
        subtitles = split_text_into_chunks(story_text, audio_clip.duration, num_chunks=20)

        # ** Title Styling **
        title_height = int(video_clip.h * 0.35)  # Move title above center
        title_bg = ColorClip(size=(video_clip.w - 100, 80), color=(0, 0, 0)).set_opacity(0.7).set_duration(audio_clip.duration)
        title_clip = TextClip(title, fontsize=60, color="white", font="Arial-Bold", stroke_color="black", stroke_width=3).set_position(("center", title_height)).set_duration(audio_clip.duration)

        # ** Captions Styling **
        subtitle_clips = [title_bg.set_position(("center", title_height)), title_clip.set_position(("center", title_height))]

        for timestamp, text in subtitles:
            subtitle_bg = ColorClip(size=(video_clip.w - 100, 120), color=(0, 0, 0)).set_opacity(0.7).set_start(timestamp).set_duration(3).set_position(("center", video_clip.h - 220))
            subtitle_text = TextClip(
                text,
                fontsize=50,
                color='yellow',
                font="Arial-Bold",
                stroke_color="black",
                stroke_width=3,
                method="caption",  # Automatically handles line breaks
                size=(video_clip.w - 120, None)  # Ensures subtitles fit within the video width
            ).set_position(("center", video_clip.h - 220)).set_start(timestamp).set_duration(3)
            
            subtitle_clips.append(subtitle_bg)
            subtitle_clips.append(subtitle_text)

        final_video = CompositeVideoClip([video_clip] + subtitle_clips)

        with tqdm(total=int(audio_clip.duration), desc="Rendering Video", unit="s") as pbar:
            def update_progress(current_frame):
                pbar.update(current_frame / final_video.fps - pbar.n)

            final_video.write_videofile(output_file, fps=24, codec="libx264", threads=4, preset="ultrafast")

        video_clip.reader.close()  # Ensure proper cleanup
        video_clip.audio.reader.close()

        print("✅ Video Created Successfully:", output_file)

    except Exception as e:
        print(f"❌ Error creating video: {e}")
