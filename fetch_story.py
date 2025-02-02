import praw
from secrets_ import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

def get_top_story(subreddit="AmItheAsshole"):
    """
    Fetch the top Reddit story from the given subreddit.
    """
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         user_agent=REDDIT_USER_AGENT)
    try:
        subreddit = reddit.subreddit(subreddit)
        top_post = next(subreddit.top(limit=1))  # Get top story
        return top_post.title + "\n" + top_post.selftext
    except Exception as e:
        print(f"⚠ Error fetching story: {e}")
        return "No story available at the moment."


# import os
# import json
# import praw
# from secrets_ import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# def get_top_story(subreddit="AmItheAsshole", cache_file="story.json"):
#     if os.path.exists(cache_file):
#         with open(cache_file, "r") as f:
#             return json.load(f)["story"]
    
#     reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
#                          client_secret=REDDIT_CLIENT_SECRET,
#                          user_agent=REDDIT_USER_AGENT)
#     try:
#         subreddit = reddit.subreddit(subreddit)
#         top_post = next(subreddit.top(limit=1))
#         story = top_post.title + "\n" + top_post.selftext
#         with open(cache_file, "w") as f:
#             json.dump({"story": story}, f)
#         return story
#     except Exception as e:
#         print(f"⚠ Error fetching story: {e}")
#         return "No story available at the moment."
