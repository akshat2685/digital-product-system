import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Verify API key
if not os.getenv("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY not found in environment or .env file.")
    sys.exit(1)

# Paths to the business templates
guide_paths = {
    'blueprint': r"C:\Users\ijain\OneDrive\Desktop\akshat\files\Digital_Product_System_5K_Month.md",
    'growth_hacks': r"C:\Users\ijain\OneDrive\Desktop\akshat\files\Growth_Hacks_Quick_Wins.md",
    'templates': r"C:\Users\ijain\OneDrive\Desktop\akshat\files\Implementation_Templates_Execution_Guide.md"
}

GUIDES = {}
for name, path in guide_paths.items():
    try:
        with open(path, 'r', encoding='utf-8') as f:
            GUIDES[name] = f.read()
    except Exception as e:
        print(f"Error reading {name} guide from {path}: {e}")
        sys.exit(1)

# Build context for the agents
GUIDES_CONTEXT = f"""
=== BUSINESS BLUEPRINT ===
{GUIDES['blueprint']}

=== VIRAL GROWTH HACKS ===
{GUIDES['growth_hacks']}

=== IMPLEMENTATION TEMPLATES ===
{GUIDES['templates']}
"""

client = genai.Client()

def ask_agent(role_prompt, task_prompt):
    system_instruction = f"""
You are an expert AI agent in the Digital Product System Swarm.
Here are the foundational blueprints, growth hacks, and implementation templates for this system:
{GUIDES_CONTEXT}

Your role: {role_prompt}
"""
    import time
    max_retries = 5
    backoff = 2
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=task_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"API Error after {max_retries} attempts: {e}")
                sys.exit(1)
            print(f"API Error (attempt {attempt+1}/{max_retries}): {e}. Retrying in {backoff} seconds...")
            time.sleep(backoff)
            backoff *= 2

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def main():
    print("Initializing Digital Product System Swarm...")
    
    # 1. Strategist Agent
    print("\n[1/4] Spawning Strategist Agent...")
    strategy_role = "You are the Chief Business Strategist. Your job is to define the niche strategy for the 'AI Automation & Operations for Agency Owners/Freelancers' business. Validate the target persona, select 5 deep pain points, and define a revenue/pricing roadmap."
    strategy_task = "Generate a markdown document outlining the Business Strategy. Include: Niche definition, Target persona profile (demographics, frustrations, desires), Top 5 Pain Points with Reddit/Twitter proof style descriptions, Revenue model structure, and Pricing breakdown (Lead Magnet, Core Product, Community, Affiliates)."
    strategy_output = ask_agent(strategy_role, strategy_task)
    
    strategy_file = "strategy/target_audience.md"
    ensure_dir(strategy_file)
    with open(strategy_file, 'w', encoding='utf-8') as f:
        f.write(strategy_output)
    print(f"Saved: {strategy_file}")

    # 2. Product Developer Agent
    print("\n[2/4] Spawning Product Developer Agent...")
    product_role = "You are the Head of Product Development. Your job is to build the actual digital products based on the Strategist's niche ('AI Automation & Operations for Agency Owners/Freelancers')."
    
    # Generate Lead Magnet
    lead_magnet_task = "Generate a complete, ready-to-read, 4-page PDF guide content titled '10 AI Prompts to Automate Client Onboarding & Reporting'. Do not use placeholders. Write the actual prompts and explanations."
    lead_magnet_output = ask_agent(product_role, lead_magnet_task)
    lead_magnet_file = "product/lead_magnet.md"
    ensure_dir(lead_magnet_file)
    with open(lead_magnet_file, 'w', encoding='utf-8') as f:
        f.write(lead_magnet_output)
    print(f"Saved: {lead_magnet_file}")

    # Generate Course Outline
    course_task = "Build a detailed course outline for a $197 core course. Provide the lesson names and goals for Modules 1-4. Also write complete, word-for-word scripts for all 3 lessons in Module 1 (hook in 15s, conversational tone, 3-5 min content length)."
    course_output = ask_agent(product_role, course_task)
    course_file = "product/course_outline.md"
    ensure_dir(course_file)
    with open(course_file, 'w', encoding='utf-8') as f:
        f.write(course_output)
    print(f"Saved: {course_file}")

    # 3. Copywriter Agent
    print("\n[3/4] Spawning Copywriter Agent...")
    copywriter_role = "You are the Conversion Copywriting Agent. Your job is to draft the email marketing sequences and the sales page copy following the blueprints exactly."
    
    # Welcome Sequence
    welcome_task = "Generate all 7 emails in the Welcome Sequence. Follow the templates in the Implementation Templates guide exactly. Write full emails, no placeholders."
    welcome_output = ask_agent(copywriter_role, welcome_task)
    welcome_file = "emails/welcome_sequence.md"
    ensure_dir(welcome_file)
    with open(welcome_file, 'w', encoding='utf-8') as f:
        f.write(welcome_output)
    print(f"Saved: {welcome_file}")

    # Launch Sequence
    launch_task = "Generate all 7 emails in the Launch Sequence. Follow the templates in the Implementation Templates guide exactly. Write full emails, no placeholders."
    launch_output = ask_agent(copywriter_role, launch_task)
    launch_file = "emails/launch_sequence.md"
    ensure_dir(launch_file)
    with open(launch_file, 'w', encoding='utf-8') as f:
        f.write(launch_output)
    print(f"Saved: {launch_file}")

    # Sales Page
    sales_task = "Write the high-converting copy using the 80/20 sales page template for the $197 core course. Include the Headline, Problem, Solution, What's Inside, Guarantee, FAQ, and CTA."
    sales_output = ask_agent(copywriter_role, sales_task)
    sales_file = "product/gumroad_sales_page.md"
    ensure_dir(sales_file)
    with open(sales_file, 'w', encoding='utf-8') as f:
        f.write(sales_output)
    print(f"Saved: {sales_file}")

    # 4. Content Creator Agent
    print("\n[4/4] Spawning Content Creator Agent...")
    creator_role = "You are the Viral Content Creator Agent. Your job is to script social media content designed for maximum virality."
    creator_task = "Write a 14-day Content Calendar. For each day, write a complete script for a YouTube Shorts/TikTok video and a Twitter thread/post. You must use the 5 viral formulas (Contradiction Hook, Wait For It, Specific Number, How I, and Past Self) throughout the calendar. Write the actual scripts and threads word-for-word, do not write summaries."
    creator_output = ask_agent(creator_role, creator_task)
    creator_file = "content/content_calendar.md"
    ensure_dir(creator_file)
    with open(creator_file, 'w', encoding='utf-8') as f:
        f.write(creator_output)
    print(f"Saved: {creator_file}")

    print("\n[SUCCESS] AI Agent Swarm has successfully completed all tasks! All digital product business assets have been generated.")

if __name__ == "__main__":
    main()
