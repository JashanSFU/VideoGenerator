import os
import requests
from secrets_ import PEXELS_API_KEY

RESULTS_DIR = "results"

def ensure_dir(directory):
    """ Ensure that a directory exists """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_stock_video(output_path=None):
    """
    Fetch a stock video from Pexels API and save it in the results directory.
    """
    ensure_dir(RESULTS_DIR)

    if output_path is None:
        output_path = os.path.join(RESULTS_DIR, "background.mp4")

    print("📹 Fetching stock video...")
    url = f"https://api.pexels.com/videos/search?query=cinematic background&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers).json()
        if "videos" not in response or len(response["videos"]) == 0:
            print("⚠ No videos found, using a default video.")
            return os.path.join(RESULTS_DIR, "default_background.mp4")
        
        video_url = response["videos"][0]["video_files"][0]["link"]

        with open(output_path, "wb") as f:
            f.write(requests.get(video_url).content)

        print(f"✅ Stock video saved as {output_path}")
        return output_path

    except Exception as e:
        print(f"⚠ Error downloading video: {e}. Using default video.")
        return os.path.join(RESULTS_DIR, "default_background.mp4")


# import os
# import json
# import requests
# from secrets_ import PEXELS_API_KEY

# def get_stock_video(cache_file="video_path.json"):
#     if os.path.exists(cache_file):
#         with open(cache_file, "r") as f:
#             return json.load(f)["video_path"]
    
#     print("📹 Fetching stock video...")
#     url = f"https://api.pexels.com/videos/search?query=cinematic background&per_page=1"
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
#         with open(cache_file, "w") as f:
#             json.dump({"video_path": video_path}, f)
#         return video_path
#     except Exception as e:
#         print(f"⚠ Error downloading video: {e}. Using default video.")
#         return "default_background.mp4"
