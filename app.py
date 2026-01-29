from flask import Flask, request, jsonify
from core import load_assets, predict_intent, call_gemini

app = Flask(__name__)

model, words, classes = load_assets()

@app.route("/analyze", methods=["GET"])
def analyze():
    text = request.args.get("text")
    if not text:
        return jsonify({"error": "text query param required"}), 400

    intent, confidence = predict_intent(text, model, words, classes)
    response = call_gemini(text, intent, confidence)

    return jsonify({
        "input": text,
        "intent": intent,
        "confidence": confidence,
        "response": response
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
