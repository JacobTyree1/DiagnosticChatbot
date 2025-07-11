from collections import defaultdict
from nltk.stem import WordNetLemmatizer
import string
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import csv
import math
import requests
import logging
import ollama

# ========== Globals ==========
lemmatizer = WordNetLemmatizer()
symptom_disease_map = defaultdict(set)
disease_to_symptoms = defaultdict(set)
symptom_to_disease_count = defaultdict(int)


# ========== Load Symptom to Disease Map ==========
def load_symptom_disease_map(path="symptom_disease_map.json"):
    global symptom_disease_map, disease_to_symptoms, symptom_to_disease_count, idf_scores

    with open(path) as f:
        raw_map = json.load(f)
        for symptom, diseases in raw_map.items():
            for disease in diseases:
                symptom_disease_map[symptom].add(disease)
                disease_to_symptoms[disease].add(symptom)
            symptom_to_disease_count[symptom] = len(diseases)
    total_diseases = len(disease_to_symptoms)
    idf_scores = {
        symptom: math.log(total_diseases / (1 + symptom_to_disease_count[symptom]))
        for symptom in symptom_to_disease_count
    }


load_symptom_disease_map()


# with open("symptom_disease_map.json") as f:
#     raw_map = json.load(f)
#     for symptom, diseases in raw_map.items():
#         for disease in diseases:
#             symptom_disease_map[symptom].add(disease)
#             disease_to_symptoms[disease].add(symptom)
#
#         symptom_to_disease_count[symptom] = len(diseases)
#
#     total_diseases = len(disease_to_symptoms)
#     idf_scores = {
#         symptom: math.log(total_diseases / (1 +  symptom_to_disease_count[symptom]))
#         for symptom in symptom_to_disease_count
#     }

# ========== Normalization Functions ==========

def normalize(symptom):
    symptom = symptom.lower().replace('-', ' ').replace('_', ' ')
    symptom = symptom.translate(str.maketrans('', '', string.punctuation))
    return lemmatizer.lemmatize(symptom.strip())


def lemmatize_sentence(text):
    words = text.split()
    lemmatized = [lemmatizer.lemmatize(w) for w in words]
    return ' '.join(lemmatized)



# ========== Ollama Integration ==========
def query_ollama(prompt, model="mistral"):
    try:
        logging.info("Calling Ollama with model: %s", model)
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        logging.info("Ollama Responded Successfully")
        return response['message']['content']
    except Exception as e:
        logging.error(f"Ollama Error: {str(e)}")
        return ""


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


# ========== Optional Fallback ==========
def parse_symptoms(text):
    try:
        symptoms = parse_symptoms_with_ollama(text)
        if symptoms:
            return symptoms
    except Exception as e:
        logging.warning(f"Ollama failed. Falling back to manual parser: {e}")

        text = lemmatize_sentence(text)
        return [normalize(w) for w in text.split()]
# ========== Disease Matching Functions ==========

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


# ========== Urgency Estimation ==========

def get_urgency(score):
    if score >= 1.5:
        return "High"
    elif score >= 0.8:
        return "Moderate"
    elif score > 0:
        return "Low"
    return "Unknown"




# ========== Wrapper for Prediction ==========

def predict_diseases(text, top_k=5):
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


# ========== Test Run ==========

if __name__ == "__main__":
    sample_input = "chills, vomiting, upset stomach, breathlessness"
    result = predict_diseases(sample_input)
    print(json.dumps(result, indent=2))
