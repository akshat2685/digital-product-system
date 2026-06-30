import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Set up paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")
CLIENT_SECRETS_PATH = os.path.join(BASE_DIR, "client_secrets.json")

# Scopes required for uploading videos to YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    credentials = None
    
    # Load previously saved credentials if they exist
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            credentials = pickle.load(token)
            
    # If there are no valid credentials, run the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing YouTube OAuth credentials...")
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_PATH):
                raise FileNotFoundError(
                    f"client_secrets.json not found at {CLIENT_SECRETS_PATH}. "
                    "Please download it from Google Cloud Console to enable YouTube uploads."
                )
            
            print("Authenticating with YouTube API via OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_PATH, SCOPES)
            credentials = flow.run_local_server(port=0)
            
        # Save credentials for future runs
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(credentials, token)
            
    return build("youtube", "v3", credentials=credentials)

def upload_video_to_youtube(video_path, title, description, category_id="27", privacy_status="public"):
    """
    Uploads a video to YouTube.
    category_id "27" represents Education.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at {video_path}")
        
    print(f"Initializing upload for video: {video_path}...")
    youtube = get_authenticated_service()
    
    body = {
        "snippet": {
            "title": title[:100],  # Title limit is 100 characters
            "description": description,
            "tags": ["AI", "automation", "productivity", "marketing"],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }
    
    # Upload media
    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
        mimetype="video/*"
    )
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}% complete.")
            
    print(f"SUCCESS: Video uploaded. YouTube Video ID: {response['id']}")
    return response["id"]

def check_youtube_setup():
    return os.path.exists(CLIENT_SECRETS_PATH) or os.path.exists(TOKEN_PATH)
