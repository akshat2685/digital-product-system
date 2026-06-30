import os
import sys
import asyncio
import shutil
import edge_tts
from gradio_client import Client, handle_file

# Set up paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def generate_voiceover(text, audio_path):
    print("Generating high-quality voiceover using Microsoft Edge TTS...")
    # Use Microsoft Edge high-quality neural voice (friendly male voice)
    voice = "en-US-GuyNeural"
    
    async def run_tts():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_path)
        
    asyncio.run(run_tts())
    print(f"Voiceover audio saved to {audio_path}")

def generate_avatar_video(text, output_video_path):
    avatar_image = os.path.join(ASSETS_DIR, "avatar.png")
    output_audio_path = output_video_path.replace(".mp4", ".mp3")
    
    # 1. Verify avatar image exists
    if not os.path.exists(avatar_image):
        print(f"Error: Avatar base image not found at {avatar_image}")
        return False
        
    # 2. Generate Voiceover Audio (Microsoft Edge TTS - 100% Free & Stable)
    try:
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        generate_voiceover(text, output_audio_path)
    except Exception as e:
        print(f"Error generating voiceover: {e}")
        return False
        
    # 3. Call Hugging Face SadTalker Space via Gradio Client (Best Effort)
    success = False
    space_name = "kevinwang676/SadTalker"
    
    print(f"Connecting to Hugging Face Space: {space_name}...")
    try:
        client = Client(space_name, verbose=False)
        print("Connected! Attempting to generate talking avatar video...")
        
        # Call Gradio API with positional arguments
        result = client.predict(
            handle_file(avatar_image),                          # source_image
            handle_file(output_audio_path),                     # input_audio
            "crop",                                            # preprocess
            True,                                              # still_mode_fewer_hand_motion_works_with_preprocess_full
            False,                                             # gfpgan_as_face_enhancer
            2,                                                 # batch_size_in_generation
            "256",                                             # face_model_resolution
            0,                                                 # pose_style
            fn_index=0
        )
        
        video_path = None
        if isinstance(result, str):
            video_path = result
        elif isinstance(result, dict) and "name" in result:
            video_path = result["name"]
        elif isinstance(result, list) and len(result) > 0:
            video_path = result[0]
            
        if video_path and os.path.exists(video_path):
            os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
            shutil.copy(video_path, output_video_path)
            print(f"SUCCESS: AI Avatar Video generated and saved to {output_video_path}")
            success = True
            # We can remove the temp audio file now that video is created
            try:
                os.remove(output_audio_path)
            except:
                pass
        else:
            print("Error: Could not locate generated video file path from Hugging Face response.")
    except Exception as e:
        print(f"SadTalker Space failed or rate-limited: {e}")
        print("Gracefully falling back to audio-only asset.")
        
    if not success:
        print(f"\n[ROBUST FALLBACK] Talking head video generation skipped.")
        print(f"-> High-quality neural voiceover saved to: {output_audio_path}")
        print(f"-> Base avatar image is ready at: {avatar_image}")
        print(f"You can manually compile these assets or run a local Wav2Lip generator.\n")
        
    return success

if __name__ == "__main__":
    # Test script if run directly
    test_text = "Hello! Welcome to the automated digital product system. Let's build your autopilot business."
    test_output = os.path.join(BASE_DIR, "videos", "test_avatar.mp4")
    print("Running quick SadTalker integration test...")
    generate_avatar_video(test_text, test_output)
