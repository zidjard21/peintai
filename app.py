from openai import OpenAI
from flask import Flask, render_template, request, session  # Import session
from dotenv import load_dotenv
import json
import os
import uuid  # To generate unique session IDs
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow all origins
app.secret_key = os.getenv("FLASK_SECRET_KEY") # Required for sessions

client = OpenAI(api_key=os.getenv("API_KEY"))

assistant_level1 = client.beta.assistants.retrieve("asst_Lh3Aw7iTVVTJjnGC8DvhieD7")
assistant_level2 = client.beta.assistants.retrieve("asst_9wWZ6jvMXY47AW3sOMHOtaHt")

# Load FAQ object
with open("FAQ.json") as f:
    faq = json.load(f)

def get_faq_response(user_input, thread_id):
    """
    Sends the user input to OpenAI and gets the assistant's response.
    """
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_level1.id
        )
        # Extract and return the assistant's response
        if run.status == 'completed':
            thread_messages = client.beta.threads.messages.list(
                thread_id=thread_id
            )
            # Ensure you are getting the last message from the data attribute
            if thread_messages.data:
                last_message = thread_messages.data[0]
                return last_message.content[0].text.value  # Return the last message content
            else:
                return "No messages received."
        else:
            return run.status

    except Exception as e:
        return f"Error: {str(e)}"

def get_openai_response(user_input, thread_id):
    """
    Sends the user input to OpenAI and gets the assistant's response.
    """
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_level2.id
        )
        # Extract and return the assistant's response
        if run.status == 'completed':
            thread_messages = client.beta.threads.messages.list(
                thread_id=thread_id
            )
            # Ensure you are getting the last message from the data attribute
            if thread_messages.data:
                last_message = thread_messages.data[0]
                return last_message.content[0].text.value  # Return the last message content
            else:
                return "No messages received."
        else:
            return run.status

    except Exception as e:
        return f"Error: {str(e)}"

@app.before_request
def initialize_session():
    """
    Initialize session-specific data for each user.
    """
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())  # Generate a unique session ID
        session["messages"] = []  # Initialize an empty list for messages
        # Create a new thread and store only the thread ID in the session
        thread = client.beta.threads.create()
        session["thread_id"] = thread.id  # Store only the thread ID

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_text = request.form.get("user_input")
        if user_text:
            # Add user message to the session's conversation history
            session["messages"].append({"sender": "user", "text": user_text})

            # Get assistant response from OpenAI
            faq_response = get_faq_response(user_text, session["thread_id"])
            print(faq_response)
            if faq_response == 'None':
                assistant_response = get_openai_response(user_text, session["thread_id"])
            else:
                assistant_response = faq[int(faq_response)-1]["message"]
            session["messages"].append({"sender": "assistant", "text": assistant_response})

            # Save the session
            session.modified = True

    return render_template("index.html", messages=session["messages"])

if __name__ == "__main__":
    app.run(debug=True)