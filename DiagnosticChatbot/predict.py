from collections import defaultdict
from nltk.stem import WordNetLemmatizer
import string
import json

lemmatizer = WordNetLemmatizer()

# 1. Load symptom-to-disease mapping

with open("symptom_disease_map.json") as f:
    raw_map = json.load(f)
    symptom_disease_map = {k: set(v) for k, v in raw_map.items()}

# 2. Normalization Functions

def normalize(symptom):
    symptom = symptom.lower().replace('-', ' ').replace('_', ' ')
    symptom = symptom.translate(str.maketrans('', '', string.punctuation))
    return lemmatizer.lemmatize(symptom.strip())

def lemmatize_sentence(text):
    words = text.split()
    lemmatized = [lemmatizer.lemmatize(w) for w in words]
    return ' '.join(lemmatized)

def parse_symptoms(text):
    symptoms = set() # Watch this variable
    if "," in text and not ' ' in text:
        symptoms = {normalize(s) for s in text.split(',')}
    else:
        text = lemmatize_sentence(text)
        words = text.split()
        symptoms = {normalize(w) for w in words}
    return symptoms


# 4. Disease Matching Functions

def match_diseases(user_symptoms):
    scores = defaultdict(int)

    for symptom in user_symptoms:
        if symptom in symptom_disease_map:
            for disease in symptom_disease_map[symptom]:
                scores[disease] += 1

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# 5. Urgency Estimation

def get_urgency(score):
    if score >= 4:
        return "High"
    elif score >= 2:
        return "Moderate"
    else:
        return "Low"

# 6. Wrapper for Prediction

def predict_diseases(tet, top_k = 5):
    user_symptoms = parse_symptoms(tet)
    matches = match_diseases(user_symptoms)
    top_condition = [{'disease': d, 'score': s} for d, s in matches[:top_k]]

    # Getting the urgency based on top score
    urgency = get_urgency(matches[0][1]) if matches else "Unknown"
    suggested_action = {
        "High": "Please seek immediate medical attention.",
        "Moderate": "Consider visiting a doctor.",
        "Low": "You may monitor symptoms or use self-care.",
        "Unknown": "No matching symptoms. Please consider rephrasing."
    }[urgency]

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