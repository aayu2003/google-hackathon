
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
import os

# Store conversation history for each user in a dictionary (in production, use a DB)
chat_sessions = {}

# Google Generative AI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configuration for the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Function to get the chat session or create a new one for each user
def get_chat_session(user_id: str):
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[{"role": "system", "content": "You are a helpful assistant."}])
    return chat_sessions[user_id]



