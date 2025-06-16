# Translation logic. Use google gemini API for this.
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


def get_client():
    return genai.Client(api_key=api_key)

def translate_text(text, target_language):
    client = get_client()

    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=(
        f"Translate the following text as accurately and naturally as possible into {target_language}.\n"
        f"Only return the translated text — do not include any explanations, notes, or additional formatting.\n\n"
        f"Text:\n{text.strip()}"
    ))
    return response.text