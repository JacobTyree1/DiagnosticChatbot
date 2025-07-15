# Diagnostic Chatbot

A Flask-based diagnostic chatbot that uses NLP and machine learning to predict possible conditions from user-reported symptoms. Includes integration with Ollama for LLM-based responses and a React frontend for the UI.

## Project Setup (Backend - Flask)
1. Clone the Repository:
    git clone https://github.com/JacobTyree1/DiagnosticChatbot.git
    cd DiagnosticChatbot
2. Create a Virtual Environment:
   python -m venv venv
   source venv/Scripts/activate
3. Upgrade pip:
    python -m pip install --upgrade pip
4. Install Dependencies:
    pip install -r requirements.txt
5. Run the Flask Server:
    python app.py
## Frontend Setup (React):
Navigate to the frontend directory
cd diagnostic-chatbot-ui
npm install
npm start

### Notes: 
1. Ensure Python 3.10 or higher is installed
2. Always activate your virtual environment before running the backend
3. After adding new dependencies, run: "pip freeze > requirements.txt" to update the requirements file

## Ollama Integration:
This project integrates with Ollama for LLM-based symptom analysis
1. Install Ollama: 
   Follow the official guide: https://ollama.ai
2. Run a Model:
   Ex: 
   ollama pull llama2
   ollama run llama2
3. Test Ollama API with Python
    import ollama
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": "Hello!"}])
    print(response)
Ensure the Ollama Server is running locally before starting your Flask app.

# Tech Stack:
1. Backend: Flask, Flask-CORS, scikit-learn, pandas, nltk
2. Frontend: React, Axios
3. LLM Integration: Ollama