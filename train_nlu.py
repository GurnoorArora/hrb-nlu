import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# Check if training data is empty
if os.stat('training_data.json').st_size == 0:
    print("Training data is empty. Please add some training data before training the model.")
    exit()

# Load training data
with open('training_data.json', 'r') as file:
    training_data = json.load(file)

x_train = []  # input
y_train = []  # labels

for item in training_data:
    intent = item['intent']
    for example in item['examples']:
        x_train.append(example)
        y_train.append(intent)

# Train model
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(x_train, y_train)

# Save model
joblib.dump(model, "nlu_model.joblib")
print("Model trained and saved as nlu_model.joblib")
