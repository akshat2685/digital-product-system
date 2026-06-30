# 🚀 Autopilot Digital Product System

Run a digital product business on 100% autopilot. This system uses AI to generate content, schedule daily posts, synthesize talking avatar videos, publish newsletters, and automate sales notifications.

---

## ✨ Features

*   **🤖 AI Swarm Content:** Automatically drafts newsletters, tweets, threads, and short video scripts (powered by Gemini).
*   **📅 Auto-Scheduler:** Spacing and queueing of daily posts in a local database.
*   **🗣️ Talking AI Avatars:** Generates human-like voiceovers (Microsoft Edge TTS) and creates lip-synced videos (SadTalker).
*   **📤 Platform Publishers:** Auto-publishes to YouTube, Twitter/X, and Beehiiv.
*   **💸 Sales Webhooks:** Instantly notifies Discord of Gumroad/Stripe sales and tags subscribers in Beehiiv.
*   **🛠️ Simulation Mode:** Runs safely offline, logging simulated posts to `published_drafts.log` if keys are missing.

---

## ⚡ Quick Start (Windows)

No coding or terminal experience needed! Follow these steps:

1.  **📥 Download the Code:** Go to the top of this GitHub page, click the green **Code** button, and select **Download ZIP**. Extract (unzip) the downloaded folder onto your computer.
2.  **🐍 Install Python:** Download and install Python from [python.org/downloads](https://www.python.org/downloads/) *(make sure to check the box **"Add Python to PATH"** during installation)*.
3.  **⚙️ Run Installer:** Open your unzipped folder and double-click the file named **`install.bat`**. This will automatically set up the system.
4.  **🔑 Add API Key:** Open the newly created **`.env`** file in Notepad, paste your `GEMINI_API_KEY`, and save.
5.  **🚀 Launch System:** Double-click **`start.bat`**. You are live!

---

## 💻 Developer Commands (Mac/Linux)

### Setup
```bash
# Clone the repository
git clone https://github.com/akshat2685/digital-product-system.git
cd digital-product-system

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CLI Usage
*   **Generate Content:** `python src/orchestrator.py --generate`
*   **View Queue:** `python src/orchestrator.py --queue-list`
*   **Publish Due Items:** `python src/orchestrator.py --publish`
*   **Run Scheduler Daemon:** `python src/orchestrator.py --scheduler`
*   **Run Webhook Server:** `python src/orchestrator.py --webhook-server`

---

## 📂 File Layout

*   `install.bat` & `start.bat` — 1-click setup and run tools.
*   `src/` — Python scripts (generator, database, publisher, webhook server, uploader).
*   `product/`, `emails/`, `content/` — Pre-written blueprints, strategies, and templates.
*   `.env` — Configuration file where you paste your API keys.
*   `published_drafts.log` — Local log file of simulated posts.
