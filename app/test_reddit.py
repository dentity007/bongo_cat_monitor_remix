import praw
import os
from dotenv import load_dotenv
import time

load_dotenv()

print("Testing Reddit auth...")

try:
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_ID'),
        client_secret=os.getenv('REDDIT_SECRET'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent='script:CatJAM:v0.1 (by /u/dentity9000)'
    )
    reddit.read_only = True

    # Step 1: Test user auth
    me = reddit.user.me()
    print(f"✅ User auth: Logged in as {me.name}")

    # Step 2: Test subreddit access (use 'test' first—super public, low rate limit)
    subreddit = reddit.subreddit('test')
    print("✅ Subreddit access: Can reach r/test")

    # Step 3: Fetch hot posts
    for post in subreddit.hot(limit=3):
        print(f"Hot post: {post.title} (score: {post.score})")

    print("🎉 Full success—copy this logic to main.py!")
except Exception as e:
    print(f"❌ Error type: {type(e).__name__}")
    print(f"Details: {e}")
    if "401" in str(e):
        print("🔑 Tip: Check .env password (try manual login at reddit.com). Or disable 2FA temporarily for testing.")