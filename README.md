# Autopilot Digital Product System & Swarm Orchestrator

An end-to-end autonomous pipeline designed to run a digital product business. It generates high-performing content packages, queues them in a local SQLite database, synthesizes neural video/audio assets, publishes them to YouTube and Twitter/X, and runs a sales webhook integration server.

---

## Key Features

1.  **AI Swarm Content Generation:** Spawns specialized agents (Strategist, Developer, Copywriter, and Creator) using Gemini to draft high-converting newsletters, tweets, threads, and short-form video scripts based on validated audience pain points.
2.  **Database Queue Scheduler:** Manages daily scheduled publications in a local SQLite queue database.
3.  **AI Video Generation (100% Free):** Synthesizes neural voiceovers using Microsoft Edge TTS, and connects with Hugging Face SadTalker Spaces to auto-generate lip-synced talking head avatar videos.
4.  **Auto-Uploader & Publisher:** Interfaces with YouTube and Twitter APIs to automatically post and schedule content.
5.  **Sales Webhook Integration:** Starts a FastAPI server that handles Gumroad and Stripe sale triggers, publishes instant Discord alerts, and syncs purchaser profiles with Beehiiv tags.
6.  **Simulation Mode:** Safely logs simulated social media posts and newsletters locally (`published_drafts.log`) when API credentials are not provided.

---

## System Architecture

```
                       [Chief Business Strategist] (Gemini)
                                     ↓
                     [Head of Product / Developer] (Gemini)
                                     ↓
                    [Conversion Copywriter] (Gemini)
                                     ↓
                    [Viral Content Creator] (Gemini)
                                     ↓
                    [SQLite database (queue.db)]
                                     ↓
                             [Orchestrator CLI]
                                     ↓
        ┌────────────────────────────┼────────────────────────────┐
        ↓                            ↓                            ↓
  [Beehiiv API]                [Twitter API]                [YouTube API]
  (Newsletters)                (Posts/Threads)            (AI Avatar Shorts)
```

---

## Installation & Setup

### 🚀 Easy 1-Click Quickstart (No-Code / Windows)
If you are on Windows and want to avoid using the terminal/command line:
1.  **Install Python:** Download and install Python from [python.org/downloads](https://www.python.org/downloads/) (make sure to check the box **"Add Python to PATH"** during installation).
2.  **Run the Installer:** Double-click the file named **`install.bat`** in the project folder. This will automatically set up the virtual environment and install all required packages.
3.  **Configure API Key:** Open the newly generated **`.env`** file in Notepad, paste your `GEMINI_API_KEY`, and save the file.
4.  **Run Autopilot:** Double-click **`start.bat`**. This launches both the content scheduler and the webhook server instantly!

---

### 💻 Manual Technical Setup
For developers or macOS/Linux users:

#### Prerequisites
*   Python 3.10+
*   FFmpeg (required if compiling local video assets)

#### Step 1: Clone and Install Dependencies
1. Initialize your project directory and activate your virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configure Environment Variables
Create a `.env` file in the root folder and add the following keys:
```env
# Core Gemini Key
GEMINI_API_KEY=your_gemini_api_key

# (Optional) Twitter/X Developer API Credentials
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# (Optional) Beehiiv Email Platform Credentials
BEEHIIV_API_KEY=your_beehiiv_api_key
BEEHIIV_PUBLICATION_ID=your_publication_id

# (Optional) Discord Webhook for Sales Notifications
DISCORD_WEBHOOK_URL=your_discord_webhook_url
```

### Step 3: Configure YouTube Upload Credentials (Optional)
If you want the system to auto-upload generated avatar videos:
1. Enable the **YouTube Data API v3** in the Google Cloud Console.
2. Download your OAuth 2.0 Desktop Client JSON file.
3. Rename it to `client_secrets.json` and save it directly in the root of this project.

---

## How To Use

The [src/orchestrator.py](src/orchestrator.py) CLI is the main entry point to control the system.

### 1. Generate & Queue Content
Generates a package of fresh daily social posts and email newsletters, spacing out their scheduled times:
```bash
python src/orchestrator.py --generate
```

### 2. Check Queue Status
View all scheduled, pending, published, and failed queue items:
```bash
python src/orchestrator.py --queue-list
```

### 3. Run a Manual Publish Trigger
Publishes any pending items that are due for release:
```bash
python src/orchestrator.py --publish
```
*(If no platform API credentials are set, this runs in **Simulation Mode** and saves outputs to `published_drafts.log` and `/videos`).*

### 4. Start the Background Scheduler
Launches a background daemon that polls the queue every 60 seconds, auto-publishes due content, and auto-refills the queue with new packages when content runs low:
```bash
python src/orchestrator.py --scheduler
```

### 5. Launch the Webhook Server
Starts the FastAPI backend on port 8000 to listen for Stripe/Gumroad sales and trigger Discord notifications:
```bash
python src/orchestrator.py --webhook-server
```

---

## File Structure

```
├── assets/
│   └── avatar.png            # Headshot image for the AI avatar
├── content/
│   └── content_calendar.md   # Swarm generated calendar blueprint
├── emails/
│   ├── welcome_sequence.md   # Pre-written welcome sequences
│   └── launch_sequence.md    # Pre-written launch sequences
├── product/
│   ├── course_outline.md     # $197 core course scripts
│   ├── gumroad_sales_page.md # Sales page copy
│   └── lead_magnet.md        # Lead magnet PDF contents
├── src/
│   ├── avatar_generator.py   # Edge-TTS and SadTalker space compiler
│   ├── database.py           # SQLite queue tracking
│   ├── generator.py          # Gemini swarm generator
│   ├── orchestrator.py       # CLI and daemon runner
│   ├── publisher.py          # Socials and email poster
│   ├── webhook_server.py     # FastAPI sale webhook endpoints
│   └── youtube_uploader.py   # YouTube Data API v3 uploader
├── strategy/
│   └── target_audience.md    # Persona and pain points document
├── requirements.txt          # Python dependencies
└── .gitignore                # Git ignore files
```

---

## License
MIT License. Free for educational and solopreneur scaling use cases.
