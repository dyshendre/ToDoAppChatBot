# chatbot.py

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import requests
from langchain_groq import ChatGroq  
from dotenv import load_dotenv


load_dotenv()
# Init Langchain OpenAI chatbot
api_key="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"
llm = ChatGroq(
    model_name="llama3-8b-8192",  # or llama3-8b-8192
    temperature=0.7,
    api_key=api_key
)

def construct__auth_headers(phoneNumber):
    # access_token = ACCESS_TOKEN_SPRINGBOOT
    # url = f"http://{server_url}/jccuae/api/vendor/loginWithPhoneNumber/{phoneNumber}"
    url= f"http://localhost:8080/employees/{phoneNumber}/getEmployeeByPhoneNumber"
    response = requests.get(url)

    if response.status_code == 200:
        # Extract the access token from the response
        data = response.json()
        access_token = data["data"]
        return {"Authorization": f"Bearer {access_token}"}
    else:
        # Handle error cases
        data = response.json()
        print(data["message"])
        return data["message"]

# Map command to backend API
def handle_user_input(userPhoneNo,input_text):
    # Get authentication headers
    auth_headers = construct__auth_headers(userPhoneNo)
    if not auth_headers:
        return "Failed to authenticate. Please try again later."
    
    response = llm([HumanMessage(content=input_text)])
    ai_response = response.content.lower()

    # Basic keyword matching logic (can be enhanced)
    if "add task" in ai_response:
        task = ai_response.split("add task")[-1].strip(": ").strip()
        res = requests.post("http://localhost:8080/tasks/create", json={"title": task}, headers=auth_headers)
        return f"Task added: {task}" if res.ok else "Failed to add task."

    elif "list" in ai_response or "show" in ai_response:
        res = requests.get("http://localhost:8080/tasks", headers=auth_headers)
        tasks = res.json()
        return tasks if tasks else "No tasks found."

    elif "delete task" in ai_response:
        task = ai_response.split("delete task")[-1].strip(": ").strip()
        # You need to search and get task id first
        res = requests.get("http://localhost:8080/tasks")
        for t in res.json():
            if task.lower() in t["title"].lower():
                del_res = requests.delete(f"http://localhost:8080/tasks/{t['id']}", headers=auth_headers)
                return f"Deleted task: {task}" if del_res.ok else "Failed to delete."
        return "Task not found."

    else:
        return "Sorry, I didn’t understand that command."

if __name__ == "__main__":
    print("Chatbot started. Type your task commands below:")
    while True:
        phone = input("Enter your mobile number: ").strip()
        msg = input("You: ").strip()

        if msg.lower() in ["exit", "quit"]:
            break

        reply = handle_user_input(phone,msg)
        print("Bot:", reply)

