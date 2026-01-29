import pickle
import numpy as np
import tensorflow as tf
import google.generativeai as genai
import nltk
import os
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def build_model(input_size, output_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(1036,)),   # len(words)
        tf.keras.layers.Dense(384, activation='relu'),
        tf.keras.layers.Dense(384, activation='relu'),   # matches dense_1 weights
        tf.keras.layers.Dense(len(classes), activation='softmax')
    ])

    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    return model

def load_assets():
    with open("words.pkl", "rb") as f:
        words = pickle.load(f)
    with open("classes.pkl", "rb") as f:
        classes = pickle.load(f)

    model = build_model(len(words), len(classes))
    model.load_weights("intent.weights.h5")

    return model, words, classes

def clean_text(sentence):
    tokens = nltk.word_tokenize(sentence)
    tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens]
    return tokens


def bow(sentence, words):
    sentence_words = clean_text(sentence)
    bag = np.zeros(len(words))
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return bag


def predict_intent(text, model, words, classes):
    x = bow(text, words).reshape(1, -1)
    preds = model.predict(x)
    idx = np.argmax(preds)
    return classes[idx], float(np.max(preds))


def build_system_prompt(intent, confidence):
    return f"""
You are a psychological support assistant.

The user's emotional intent has already been classified as '{intent}'
with confidence {confidence}.

You must:
- Assume the intent classification is correct
- Respond strictly within the context of this intent
- Use the user's words to ground your response
- Be empathetic, calm, and practical
- Avoid diagnosis or medical claims
- Offer small, actionable suggestions
- Do not reclassify or question the intent
"""


def call_gemini(text, intent, confidence):
    system_prompt = build_system_prompt(intent, confidence)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )

    response = model.generate_content(text)
    return response.text.strip()
