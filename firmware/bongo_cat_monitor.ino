void setup() {
  Serial.begin(115200);
  Serial.println("CatJAM Firmware Ready!");  // For testing
  // TODO: Add LVGL/TFT setup from original Vostok project
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.startsWith("MEME:")) {
      Serial.println("MEME fired: " + cmd);  // Echo for testing—replace with animation/bubble
      // TODO: playAnimation(cmd.substring(5)); showBubble(...);
    }
    // TODO: Add TUTOR/FX parsers
  }
  delay(10);
}

import praw
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_ID'),
    client_secret=os.getenv('REDDIT_SECRET'),
    user_agent='CatJAM Monitor v1.0'
)

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