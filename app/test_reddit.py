"""
Reddit API Authentication Test Script

Tests Reddit API connectivity and authentication for the CatJAM Monitor.
This script validates that Reddit credentials are working correctly before
integrating with the main application.

Usage:
    python test_reddit.py

Environment Variables Required:
    REDDIT_ID: Reddit app client ID
    REDDIT_SECRET: Reddit app client secret
    REDDIT_USERNAME: Reddit username
    REDDIT_PASSWORD: Reddit password

Author: dentity007
Version: 1.0.0
Date: September 2025
"""

import praw
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

print("Testing Reddit auth...")

try:
    # Initialize Reddit API client with credentials from environment
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_ID'),
        client_secret=os.getenv('REDDIT_SECRET'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent='script:CatJAM:v0.1 (by /u/dentity9000)'
    )
    reddit.read_only = True  # Set to read-only mode for safety

    # =========================================================================
    # STEP 1: Test User Authentication
    # =========================================================================
    print("🔐 Testing user authentication...")
    me = reddit.user.me()
    print(f"✅ User auth: Logged in as {me.name}")

    # =========================================================================
    # STEP 2: Test Subreddit Access
    # =========================================================================
    print("🌐 Testing subreddit access...")
    # Use 'test' subreddit first - it's public and has low rate limits
    subreddit = reddit.subreddit('test')
    print("✅ Subreddit access: Can reach r/test")

    # =========================================================================
    # STEP 3: Test Content Fetching
    # =========================================================================
    print("📄 Testing content fetching...")
    # Fetch a few hot posts to verify API is working
    for post in subreddit.hot(limit=3):
        print(f"Hot post: {post.title} (score: {post.score})")

    # =========================================================================
    # SUCCESS MESSAGE
    # =========================================================================
    print("🎉 Full success—copy this logic to main.py!")

except Exception as e:
    # =========================================================================
    # ERROR HANDLING
    # =========================================================================
    print(f"❌ Error type: {type(e).__name__}")
    print(f"Details: {e}")

    # Provide specific troubleshooting tips based on error type
    if "401" in str(e):
        print("🔑 Tip: Check .env password (try manual login at reddit.com). Or disable 2FA temporarily for testing.")
    elif "403" in str(e):
        print("🚫 Tip: Check Reddit app permissions - ensure it's set as 'script' type.")
    elif "429" in str(e):
        print("⏱️ Tip: Rate limit exceeded - wait a few minutes before retrying.")
    else:
        print("💡 Tip: Check your .env file and Reddit app settings at https://www.reddit.com/prefs/apps")