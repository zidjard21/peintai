from openai import OpenAI
from flask import Flask, render_template, request, g
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("API_KEY"))

assistant = client.beta.assistants.retrieve("asst_9wWZ6jvMXY47AW3sOMHOtaHt")

# Store messages in memory for simplicity
messages = []

thread = client.beta.threads.create()

def get_openai_response(user_input):
    """
    Sends the user input to OpenAI and gets the assistant's response.
    """
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        # Extract and return the assistant's response
        if run.status == 'completed':
            thread_messages = client.beta.threads.messages.list(
                thread_id=thread.id
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
def reset_messages():
    """
    Initialize a new list of messages for each request.
    This ensures messages are cleared on every reload.
    """
    g.messages = []

@app.route("/", methods=["GET", "POST"])
def home():
    global messages

    if request.method == "POST":
        user_text = request.form.get("user_input")
        if user_text:
            # Add user message to the conversation history
            messages.append({"sender": "user", "text": user_text})

            # Get assistant response from OpenAI
            assistant_response = get_openai_response(user_text)
            messages.append({"sender": "assistant", "text": assistant_response})

    return render_template("index.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
