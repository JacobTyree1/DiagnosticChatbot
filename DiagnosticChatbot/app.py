from flask import Flask, request, jsonify
# Use predict.py file
from predict import predict_diseases
# To install dependencies from requirements.txt:
# pip install -r requirements.txt

app = Flask(__name__)

@app.route("/") # Homepage route (Whatever comes after .com)
def home(): # Homepage
    return "Smart Diagnostic Chatbot is running." # Returns something

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"Error": "Please provide a 'text' field in JSON."}), 400
    # Finish the rest of this file.


