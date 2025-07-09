from collections import defaultdict
from nltk.stem import WordNetLemmatizer
import string
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import csv
import math
import requests

lemmatizer = WordNetLemmatizer()

symptom_disease_map = defaultdict(set)
disease_to_symptoms = defaultdict(set)
symptom_to_disease_count = defaultdict(int)





# 1. Load symptom-to-disease mapping

with open("symptom_disease_map.json") as f:
    raw_map = json.load(f)
    for symptom, diseases in raw_map.items():
        for disease in diseases:
            symptom_disease_map[symptom].add(disease)
            disease_to_symptoms[disease].add(symptom)

        symptom_to_disease_count[symptom] = len(diseases)

    total_diseases = len(disease_to_symptoms)
    idf_scores = {
        symptom: math.log(total_diseases / (1 +  symptom_to_disease_count[symptom]))
        for symptom in symptom_to_disease_count
    }

# 2. Normalization Functions

def normalize(symptom):
    symptom = symptom.lower().replace('-', ' ').replace('_', ' ')
    symptom = symptom.translate(str.maketrans('', '', string.punctuation))
    return lemmatizer.lemmatize(symptom.strip())

def lemmatize_sentence(text):
    words = text.split()
    lemmatized = [lemmatizer.lemmatize(w) for w in words]
    return ' '.join(lemmatized)

# def parse_symptoms(text):
#     print("Raw input:", text)
#     if "," in text:
#         symptoms = {normalize(s) for s in text.split(',')}
#     else:
#         text = lemmatize_sentence(text)
#         words = text.split()
#         symptoms = {normalize(w) for w in words}
#
#     print("Normalized symptoms: ", symptoms)
#     return list(symptoms)

def query_ollama(prompt, model="mistral"):

    response = requests.post("https://localhost:11434/api/generate",
                             json={"model":model, "prompt":prompt, "stream": False})
    response.raise_for_status()
    return response.json()["response"]


def parse_symptoms_with_ollama(text):
    prompt = (
        "Extract a comma-separated list of symptoms from the following sentence.\n"
        "Respond only with a comma-separated list (no extra text):\n\n"
        f"{text}"
    )
    response = query_ollama(prompt)
    symptoms = [normalize(s.strip()) for s in response.split(",") if s.strip()]
    print("LLM-extracted symptoms:", symptoms)
    return symptoms


# 4. Disease Matching Functions

def match_diseases(user_symptoms):
    scores = defaultdict(float)

    for symptom in user_symptoms:
        if symptom in symptom_disease_map:
            idf_weight = idf_scores.get(symptom, 0.0)
            for disease in symptom_disease_map[symptom]:
                scores[disease] += idf_weight

    for disease in scores:
        total_symptoms = len(disease_to_symptoms[disease]) or 1
        scores[disease] /= total_symptoms


    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# 5. Urgency Estimation

def get_urgency(score):
    if score >= 1.5:
        return "High"
    elif score >= 0.8:
        return "Moderate"
    elif score > 0:
        return "Low"
    return "Unknown"

# 6. Wrapper for Prediction

def predict_diseases(text, top_k = 5):
    user_symptoms = parse_symptoms_with_ollama(text)
    matches = match_diseases(user_symptoms)

    if not matches:
        return {
            "top_conditions": [],
            "urgency_level": "Unknown",
            "suggested_action": "No matching symptoms. Please consider rephrasing."
        }


    top_condition = [{'disease': d, 'score': round(s, 4)} for d, s in matches[:top_k]]

    # Getting the urgency based on top score
    urgency = get_urgency(matches[0][1])


    suggested_action = {
        "High": "Please seek immediate medical attention.",
        "Moderate": "Consider visiting a doctor.",
        "Low": "You may monitor symptoms or use self-care.",
        "Unknown": "No matching symptoms. Please consider rephrasing."
    }.get(urgency, "Unknown action")

    return {
        "top_conditions": top_condition,
        "urgency_level": urgency,
        "suggested_action": suggested_action
    }

# 7. Test Run:

if __name__ == "__main__":
    sample_input = "vomiting, diarrhea, upset stomach, chills, breathlessness"
    result = predict_diseases(sample_input)
    print(json.dumps(result, indent=2))