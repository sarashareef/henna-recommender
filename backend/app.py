from flask import Flask, request, jsonify, send_from_directory
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os, json
import numpy as np


app = Flask(__name__, static_folder="../static")
base_dir = "../henna_images"

all_metadata = []
all_embeddings = []

for folder in os.listdir(base_dir):
    metadata_path = os.path.join(base_dir, folder, "metadata.json")
    if os.path.isfile(metadata_path):
        with open(metadata_path) as f: 
            meta = json.load(f)
            for entry in meta: 
                full_path = os.path.join(folder, entry["filename"])
                all_metadata.append({
                    "filename": entry["filename"],
                    "description": entry["description"],
                    "full_path": full_path
                })
all_texts = [entry["description"] for entry in all_metadata]

def cosine_sim(a,b): 
    return np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))

@app.route("/")
def home():
    print("Looking for:", os.path.join(app.static_folder, "index.html"))
    return send_from_directory(app.static_folder, "index.html")

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory("../henna_images", filename)

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

user_sessions = {}
@app.route("/recommend", methods=["POST"])
def recommend():
    query = request.json["query"]
    user_id = request.json.get("user_id", "default")  # use a user_id to separate sessions

    if user_id not in user_sessions or user_sessions[user_id]["query"] != query:
        vectorizer = CountVectorizer()
        texts = all_texts + [query]
        vectors = vectorizer.fit_transform(texts)

        input_vector = vectors[-1]
        description_vectors = vectors[:-1]

        similarities = cosine_similarity(input_vector, description_vectors)[0]
        ranked_indices = np.argsort(similarities)[::-1]

        # Store results in session
        user_sessions[user_id] = {
            "query": query,
            "indices": ranked_indices.tolist(),
            "position": 0
        }

    session = user_sessions[user_id]
    start = session["position"]
    end = start + 3
    session["position"] = end  # update position

    top_k = session["indices"][start:end]
    results = [all_metadata[i] for i in top_k]

    for img in results:
        img["url"] = f"/images/{img['full_path']}"

    return jsonify(results)

if __name__ == '__main__': 
    app.run()