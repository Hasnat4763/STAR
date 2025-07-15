import praw
from dotenv import load_dotenv
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from random import randint

load_dotenv(".env")
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))


def fetch_memes_from_reddit(channels):
    subreddit = reddit.subreddit("astronomymemes")
    posts = [x for x in subreddit.hot(limit=100) if not x.stickied and x.url.endswith(('.jpg', '.png', '.gif'))]
    if not posts:
        print("No suitable posts found.")
        return
    post = posts[randint(0, len(posts) - 1)]
    
    try:
        client.chat_postMessage(
            channel=channels,
            blocks=[
                   {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*<{post.url}|{post.title}> *\nFrom r/astronomymemes"
                    }
                    },
                    {
                    "type": "image",
                    "image_url": post.url,
                    "alt_text": post.title
                    }
                    ]
                )
    except SlackApiError as e:
        print(f"Error posting to Slack: {e.response['error']}")
