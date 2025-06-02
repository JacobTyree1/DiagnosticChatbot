from flask import Flask, request, jsonify
from flask_cors import CORS
# Use predict.py file
from predict import predict_diseases
import logging

# To install dependencies from requirements.txt:
# pip install -r requirements.txt

app = Flask(__name__)
CORS(app) # Enabled for all routes

@app.route("/") # Homepage route (Whatever comes after .com)
def home(): # Homepage
    return "Smart Diagnostic Chatbot is running." # Returns something


def validate_input(data):
    if not data or "text" not in data:
        return False, "Missing 'text' field in input JSON"
    if not isinstance(data['text'], str) or len(data['text'].strip()) == 0:
        return False, "'text' field must be a non-empty string"
    return True, None

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

if __name__ == "__main__":
    app.run(debug=True) # Turn this off when you fully roll it out


