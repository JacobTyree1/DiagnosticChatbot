import subprocess
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from predict import predict_diseases
import logging

# To install dependencies from requirements.txt:
# pip install -r requirements.txt


app = Flask(__name__)
CORS(app) # Enabled for all routes

def is_ollama_running():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

# ========== Ollama Helper Functions ==========

def start_ollama():
    print("Starting Ollama Service...")
    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait_for_model(model_name, timeout=60):
    logging.info(f"Waiting for model '{model_name}' to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.post("http://localhost:11434/api/show", json={"model": model_name}, timeout=5)
            if response.status_code == 200:
                logging.info(f"Model '{model_name}' is ready.")
                return True
        except requests.RequestException:
            pass
        time.sleep(2)
    logging.error(f"Model '{model_name}' did not load within {timeout} seconds")
    return False

def model_exists(model_name):
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200 and model_name in response.text:
            return True
        return False
    except requests.RequestException:
        return False

# ========== Configure logging ==========
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")




# ========== Validation ==========
def validate_input(data):
    if not data or "text" not in data:
        return False, "Missing 'text' field in input JSON"
    if not isinstance(data['text'], str) or len(data['text'].strip()) == 0:
        return False, "'text' field must be a non-empty string"
    return True, None


# ========== Routes ==========

@app.route("/") # Homepage route (Whatever comes after .com)
def home(): # Homepage
    return "Smart Diagnostic Chatbot is running." # Returns something

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "version": "1.0"})

@app.route("/about")
def about():
    return jsonify({
        "project": "Smart Diagnostic Chatbot",
        "description": "A Flask-based API that uses traditional NLP and LLMs to match symptoms to possible diseases",
        "author": "Jacob Tyree",
    })
@app.route("/predict", methods=["POST"]) # Routes the POST to the predict method
def predict():
    data = request.get_json()
    print("Request received:", data)
    is_valid, error = validate_input(data)

    if not is_valid:
        logging.warning(f"Invalid input: {error}")
        print("Validation failed: ", error)
        return jsonify({"error": error}), 400

    input_text = data['text']
    print("Raw user input: ", input_text)
    logging.info(f"Received input: {input_text}")

    try:
        result = predict_diseases(input_text)
        print("Final result: ", result)
        logging.info(f"Prediction Result: {result}")
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error during prediction {str(e)}")
        print("Exception during prediction: ", str(e))
        return jsonify({"error": str(e)}), 500


# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()
#     message = data.get("message", "").strip()
#     if not message:
#         return jsonify({"error": "Message is required"}), 400
#     logging.info(f"Chat Prompt Received: {message}")
#     reply = query_ollama(message)
#     return jsonify({"response": reply})

# Chat function that can be worked in later
# Will function either in a new window, or in the same window. New window would probably be best for learning
# Could have a separate button that allows the user to click to further chat about their symptoms.
# This could end up using Ollama as a whole and not having Ollama pull symptoms and be limited to that.

if __name__ == "__main__":
    if not is_ollama_running():
        logging.info("Ollama service not running. Starting now...")
        start_ollama()
        for _ in range(10):
            if is_ollama_running():
                logging.info("Ollama service started successfully")
                break
            time.sleep(1)
        else:
            logging.error("Failed to start Ollama service")
            exit(1)

    if not wait_for_model('mistral'):
        logging.error("Ollama model failed to load. Exiting")
        exit(1)
    app.run(debug=True, threaded=True) # Turn this off when you fully roll it out


