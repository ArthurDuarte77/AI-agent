import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
from actions import get_response_time
from gmail import read_emails, send_email
from prompts import system_prompt
from google_calendar import list_events, list_tasks, create_task, create_event
from whatsapp import getMessagesUnread, send_messages
from json_helpers import extract_json

# Load environment variables
load_dotenv()

history = [
    {"role": "model", "parts":[ system_prompt]},
]

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

safety_settings = {
    genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
    genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
    genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
    genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
}

# Create an instance of the Gemini model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)


def generate_text_with_conversation(history, messages, model_name="gemini-2.0-flash-exp"):
    chat_session = model.start_chat(
        history=history
    )
    response = chat_session.send_message(messages)
    history.append({"role": "user", "parts": [messages]})
    history.append({"role": "model", "parts": [response.text]})
    return response.text

#Available actions are:
available_actions = {
    "get_response_time": get_response_time,
    "read_emails": read_emails,
    "get_events": list_events,
    "list_tasks": list_tasks,
    "create_task": create_task,
    "create_event": create_event,
    "get_messages": getMessagesUnread,
    "send_messages": send_messages,
    "send_email": send_email
}


def process_user_input(user_prompt):
    """Processes user input, including function calls."""
    
    response = generate_text_with_conversation(history, user_prompt)
    print("Bot:", response)
    if "Pensamento:" not in response:
        requests.post("https://ecommerceflow.com.br/waha/api/sendText", {
            "chatId": "553791332517@c.us",
            "text": f"{response}",
            "session": "default"
        })

    json_function = extract_json(response)

    if json_function:
        function_name = json_function[0]['function_name']
        function_parms = json_function[0]['function_parms']
        if function_name not in available_actions:
            function_result_message = f"Resposta_da_Ação: So responda a pergunta do usuario"
            process_user_input(function_result_message) 
        else:
            print(f" -- running {function_name} {function_parms}")
            action_function = available_actions[function_name]
            #call the function
            result = action_function(**function_parms)
            function_result_message = f"Resposta_da_Ação: {result}"
            print(function_result_message)
            process_user_input(function_result_message)
    


if __name__ == "__main__":
    print("Olá! Sou seu assistente. Como posso ajudar?")
    while True:
        user_prompt = input("Você: ")
        if user_prompt.lower() in ["sair", "tchau", "adeus"]:
            print("Bot: Tchau! Até a próxima.")
            break
        process_user_input(user_prompt)