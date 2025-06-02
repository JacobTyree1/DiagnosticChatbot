from collections import defaultdict
from nltk.stem import WordNetLemmatizer
import string
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import csv

lemmatizer = WordNetLemmatizer()
tfidf = TfidfVectorizer()


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
    print("Raw input:", text)
    if "," in text:
        symptoms = {normalize(s) for s in text.split(',')}
    else:
        text = lemmatize_sentence(text)
        words = text.split()
        symptoms = {normalize(w) for w in words}

    print("Normalized symptoms: ", symptoms)
    print("Type: ", type(symptoms))
    return list(symptoms)


# 4. Disease Matching Functions

def match_diseases(user_symptoms):
    scores = defaultdict(int)
    for symptom in user_symptoms:
        if symptom in symptom_disease_map:
            for disease in symptom_disease_map[symptom]:
                scores[disease] += 1
    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    scores_reduced = scores[:5]
    score_normalization(scores_reduced)
    return scores



# 4a. Score Normalization

def score_normalization(scores_reduced):
    # Scores_reduced is actually a tuple of type list
    # Following this logic: normalized_score = (matching_symptoms_count) / (total_symptoms_for_disease

    # Merging training and test together
    # file_names = ['normalized_train.csv', 'normalized_test.csv']
    #
    # merged_data = pd.DataFrame()
    #
    # for filename in file_names:
    #     df = pd.read_csv(filename)
    #     merged_data = pd.concat([merged_data, df], ignore_index=True)
    # merged_data.to_csv('normalized_merge.csv', index=

    # The above code doesn't need to be run unless the dataset is changed

    # Step by step logic:
    # 1. Save diseases as their stand-alone list
    diseases = [item[0] for item in scores_reduced]
    # 2. Create a disease_to_symptoms set to save information
    disease_to_symptoms = defaultdict(set)
    # 3. Add the ['text'] aspect of the symptom_disease_map to the disease_to_symptoms
    for symptom, diseases in symptom_disease_map.items():
        for disease in diseases:
            disease_to_symptoms[disease].add(symptom)

    # 4. Collect total symptoms based on the top 5 results
    normalized = []
    for disease, score in scores_reduced:
        total_symptoms = len(disease_to_symptoms[disease]) or 1 # Avoiding div by 0
        # 5. Divide by the score that was given to the disease and multiply by 100
        normalized_score = (score / total_symptoms) * 100
        # 6. Append to the newly created list that acts as a tuple
        normalized.append((disease, normalized_score))

    print(normalized)
    # This will be used in the UI as the confidence score for the progress bar.




# 4b. TF-IDF Symptom Weighting:






# 5. Urgency Estimation

def get_urgency(score):
    if score >= 4:
        return "High"
    elif score >= 2:
        return "Moderate"
    else:
        return "Low"

# 6. Wrapper for Prediction

def predict_diseases(text, top_k = 5):
    user_symptoms = parse_symptoms(text)
    matches = match_diseases(user_symptoms)

    if not matches:
        return {
            "top_conditions": [],
            "urgency_level": "Unknown",
            "suggested_action": "No matching symptoms. Please consider rephrasing."
        }


    top_condition = [{'disease': d, 'score': s} for d, s in matches[:top_k]] # Prints the top 5

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