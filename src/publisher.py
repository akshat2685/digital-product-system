import os
import requests
from datetime import datetime
from dotenv import load_dotenv

import src.database as db

# Load environment variables
load_dotenv()

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "published_drafts.log")

def write_to_simulation_log(item_id, item_type, content):
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"""
==================================================
[SIMULATION PUBLISHED]
ID: {item_id}
Type: {item_type}
Time: {timestamp} UTC
--------------------------------------------------
{content}
==================================================
"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def publish_to_beehiiv(content):
    api_key = os.getenv("BEEHIIV_API_KEY")
    pub_id = os.getenv("BEEHIIV_PUBLICATION_ID")
    if not api_key or not pub_id:
        raise ValueError("Missing BEEHIIV_API_KEY or BEEHIIV_PUBLICATION_ID in environment.")
        
    url = f"https://api.beehiiv.com/v2/publications/{pub_id}/posts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    subject = "Daily AI Automation Insights"
    body = content
    if content.startswith("Subject:"):
        lines = content.split("\n", 1)
        subject = lines[0].replace("Subject:", "").strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        
    data = {
        "title": subject,
        "body": body,
        "status": "draft"  # Created as draft for user safety & review
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def publish_to_twitter(content):
    # Check for Twitter developer API credentials
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        raise ValueError("Missing Twitter/X API credentials in environment.")
        
    # Attempt to import tweepy
    try:
        import tweepy
    except ImportError:
        raise ImportError("tweepy package is not installed. Run 'pip install tweepy' to enable live Twitter publishing.")
        
    # Standard Twitter API v2 Tweet posting
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    # If the content contains '---', it's a thread
    if "---" in content:
        tweets = [t.strip() for t in content.split("---") if t.strip()]
        # Post thread
        previous_tweet_id = None
        for i, tweet in enumerate(tweets):
            if i == 0:
                response = client.create_tweet(text=tweet)
            else:
                response = client.create_tweet(text=tweet, in_reply_to_tweet_id=previous_tweet_id)
            previous_tweet_id = response.data['id']
    else:
        client.create_tweet(text=content)

def publish_due_items():
    pending_items = db.get_pending_items()
    if not pending_items:
        print("No pending content items due for publishing at this time.")
        return
        
    print(f"Found {len(pending_items)} due items. Attempting to publish...")
    
    for item_id, item_type, content, scheduled_time in pending_items:
        print(f"\nProcessing item {item_id} [{item_type}] scheduled for {scheduled_time}...")
        
        try:
            if item_type == "email_newsletter":
                try:
                    publish_to_beehiiv(content)
                    db.mark_as_published(item_id)
                    print(f" Successfully posted draft newsletter to Beehiiv API.")
                except ValueError:
                    # Fallback to simulation
                    write_to_simulation_log(item_id, item_type, content)
                    db.mark_as_published(item_id)
                    print(f" [Simulation] Logged newsletter to published_drafts.log (Missing Beehiiv API keys).")
                    
            elif item_type in ["twitter_post", "twitter_thread"]:
                try:
                    publish_to_twitter(content)
                    db.mark_as_published(item_id)
                    print(f" Successfully published tweet/thread to Twitter/X API.")
                except (ValueError, ImportError) as e:
                    # Fallback to simulation
                    write_to_simulation_log(item_id, item_type, content)
                    db.mark_as_published(item_id)
                    print(f" [Simulation] Logged tweet/thread to published_drafts.log ({str(e)}).")
                    
            elif item_type == "youtube_shorts_script":
                import src.avatar_generator as avatar
                import src.youtube_uploader as yt
                
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                video_filename = f"video_{item_id}.mp4"
                video_path = os.path.join(base_dir, "videos", video_filename)
                
                print(f"Starting automatic AI avatar generation for item {item_id}...")
                video_created = avatar.generate_avatar_video(content, video_path)
                
                if video_created:
                    # Check if YouTube setup is available
                    if yt.check_youtube_setup():
                        try:
                            title = f"AI Automation Daily Hack #{item_id}"
                            desc = f"{content}\n\nCheck out the free automation guide in the channel description!"
                            yt.upload_video_to_youtube(video_path, title, desc)
                            db.mark_as_published(item_id)
                            print(f" Successfully generated avatar video and uploaded to YouTube.")
                        except Exception as e:
                            db.mark_as_failed(item_id, f"Video generated but YouTube upload failed: {e}")
                            print(f" Video generated at {video_path} but YouTube upload failed: {e}")
                    else:
                        db.mark_as_published(item_id)
                        print(f" Successfully generated talking avatar video locally at {video_path}.")
                        print(f" (YouTube credentials not configured, skipping auto-upload).")
                else:
                    # Fallback to simulation log
                    write_to_simulation_log(item_id, item_type, content)
                    db.mark_as_published(item_id)
                    print(f" [Simulation] Talking avatar failed to generate. Logged script to published_drafts.log.")
                
            else:
                db.mark_as_failed(item_id, f"Unknown item type: {item_type}")
                print(f" Unknown item type: {item_type}. Marked as failed.")
                
        except Exception as e:
            db.mark_as_failed(item_id, str(e))
            print(f" Error publishing item {item_id}: {e}")
