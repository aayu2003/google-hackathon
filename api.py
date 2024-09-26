from fastapi import FastAPI
import google.generativeai as genai

# Initialize FastAPI app
app = FastAPI()

# Store conversation history for each user in a dictionary (in production, use a DB)
chat_sessions = {}

# Google Generative AI API key
api_key = "AIzaSyCttE7CHlvxpD3o4bNMHi7Sj52IHPbfaTU"
genai.configure(api_key=api_key)

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
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]

# API endpoint to handle GET chat messages via query params
@app.get("/chat/")
async def chat(user_id: str, message: str):
    # Get or create the chat session for this user
    chat_session = get_chat_session(user_id)

    # Send the user's message to the model and get the response
    response = chat_session.send_message(message)

    # Return the bot's response
    return {"response": response.text}

# Command to run the server: uvicorn <script_name>:app --reload
