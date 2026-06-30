import os
import sys
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types
from dotenv import load_dotenv

import src.database as db

# Load environment variables
load_dotenv()

# Define Pydantic Models for Structured Output
class QueuedItem(BaseModel):
    item_type: str = Field(description="Must be one of: 'twitter_post', 'twitter_thread', 'youtube_shorts_script', 'email_newsletter'")
    content: str = Field(description="The actual text content of the post. For 'twitter_thread', use '---' to separate individual tweets in the thread.")

class DailyContentPackage(BaseModel):
    items: List[QueuedItem] = Field(description="A list of generated content items for the day.")

def load_context():
    # Workspace root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    audience_path = os.path.join(base_dir, "strategy", "target_audience.md")
    growth_hacks_path = r"C:\Users\ijain\OneDrive\Desktop\akshat\files\Growth_Hacks_Quick_Wins.md"
    templates_path = r"C:\Users\ijain\OneDrive\Desktop\akshat\files\Implementation_Templates_Execution_Guide.md"
    
    context = {}
    
    # Load Target Audience Strategy
    if os.path.exists(audience_path):
        with open(audience_path, "r", encoding="utf-8") as f:
            context["audience"] = f.read()
    else:
        context["audience"] = "Niche: AI Automation & Operations for Agency Owners & Freelancers"
        
    # Load Growth Hacks & Templates
    for name, path in [("growth_hacks", growth_hacks_path), ("templates", templates_path)]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                context[name] = f.read()
        except Exception as e:
            context[name] = f"Error loading template file at {path}: {e}"
            
    return context

def generate_daily_content():
    print("Loading strategy and templates context...")
    context = load_context()
    
    # Verify API key
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in environment or .env file.")
        return False
        
    client = genai.Client()
    
    system_instruction = f"""
You are the lead Copywriter and Social Media manager in the Digital Product System Swarm.
Your target audience is defined by the following strategy:
=== TARGET AUDIENCE STRATEGY ===
{context['audience']}

You must use the formulas, style, and structures outlined here:
=== VIRAL GROWTH HACKS ===
{context['growth_hacks']}

=== IMPLEMENTATION TEMPLATES ===
{context['templates']}

Your task is to generate a package of daily content to queue for publishing.
You must output exactly 4 items:
1. A single Twitter Post (using a Contradiction Hook or Specific Number formula). Keep under 280 chars.
2. A Twitter Thread (3-5 tweets, separated by '---' on a new line). Focus on a framework or before/after transformation.
3. A YouTube Shorts video script (word-for-word spoken text, 45-60 seconds read time, with visual cues in brackets, e.g. [Show screen]).
4. An Email Newsletter (educational value, myth-busting or solving a blocker, conversational tone, subject line at top).

Be highly creative, do not use placeholder text, and write full production-ready copy.
"""

    prompt = "Generate today's content package for the AI Automation niche."
    
    print("Calling Gemini API to generate content package...")
    
    # Retry loop for Gemini call
    import time
    max_retries = 3
    backoff = 2
    response_data = None
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=DailyContentPackage,
                )
            )
            # Parse response
            import json
            response_data = json.loads(response.text)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to generate content: {e}")
                return False
            print(f"API Error (attempt {attempt+1}/{max_retries}): {e}. Retrying in {backoff} seconds...")
            time.sleep(backoff)
            backoff *= 2

    if not response_data or "items" not in response_data:
        print("Error: Received invalid response structure from Gemini.")
        return False

    print(f"Successfully generated {len(response_data['items'])} items. Queueing them...")
    
    # Base scheduled time starting now
    base_time = datetime.utcnow()
    
    # Spacing out items throughout the day:
    # 1. Twitter Post: +2 hours
    # 2. Twitter Thread: +5 hours
    # 3. YouTube Shorts: +8 hours
    # 4. Email Newsletter: +12 hours
    delays = {
        "twitter_post": 2,
        "twitter_thread": 5,
        "youtube_shorts_script": 8,
        "email_newsletter": 12
    }
    
    for item in response_data["items"]:
        item_type = item["item_type"]
        content = item["content"]
        
        delay_hrs = delays.get(item_type, 1)
        scheduled_time = (base_time + timedelta(hours=delay_hrs)).isoformat()
        
        db.add_to_queue(item_type, content, scheduled_time)
        print(f" Queued [{item_type}] scheduled for {scheduled_time} UTC")
        
    return True
