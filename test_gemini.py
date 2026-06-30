import os
import dotenv
from google import genai

dotenv.load_dotenv()
client = genai.Client()
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='test',
    )
    print("Success! Response:", response.text)
except Exception as e:
    print("Failed. Error:", e)
