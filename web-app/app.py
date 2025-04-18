"""main app.py for flask"""

from flask import Flask, render_template, request, jsonify
from bson.errors import InvalidId
from bson.objectid import ObjectId
import pymongo

app = Flask(__name__)

# mongodb connection
client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["bitebuzz"]
collection = db["reviews"]


@app.route("/")
def index():
    """
    sends data to the db
    """
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_review():
    """
    receives transcribed text from frontend and stores it in the DB
    """
    review_text = request.json.get("text")
    if not review_text:
        return jsonify({"error": "No text provided"}), 400

    doc = {"text": review_text, "processed": False}
    result = collection.insert_one(doc)
    return jsonify({"id": str(result.inserted_id)})


@app.route("/result/<review_id>")
def get_result(review_id):
    """
    returns processed analysis results if available
    """
    try:
        _id = ObjectId(review_id)
    except (InvalidId, TypeError, ValueError):
        return jsonify({"error": "Invalid review ID"}), 400

    review = collection.find_one({"_id": _id})
    if not review:
        return jsonify({"error": "Not found"}), 404
    if not review.get("processed"):
        return jsonify({"status": "processing"}), 202

    return jsonify(
        {
            "text": review["text"],
            "sentiment": review["sentiment"],
            "suggestion": review["suggestion"],
            "category": review["category"],
            "polarity": review["polarity"],
            "subjectivity": review["subjectivity"],
        }
    )


@app.route("/logs")
def get_logs():
    """
    returns all logs in db
    """
    logs = collection.find({"processed": True})
    result = []
    for doc in logs:
        result.append(
            {
                "text": doc.get("text"),
                "sentiment": doc.get("sentiment"),
                "suggestion": doc.get("suggestion"),
                "category": doc.get("category"),
                "polarity": doc.get("polarity"),
                "subjectivity": doc.get("subjectivity"),
                "date": doc.get("date"),
            }
        )
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
