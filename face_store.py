import json
import os
import numpy as np

FACES_FILE = "known_faces.json"
PROCESSED_FILE = "processed_images.json"


def load_faces():
    if not os.path.exists(FACES_FILE):
        return {}

    with open(FACES_FILE, "r") as f:
        data = json.load(f)

    for name in data:
        data[name] = [np.array(e) for e in data[name]]

    return data


def save_faces(face_dict):
    serializable = {}
    for name, embeddings in face_dict.items():
        serializable[name] = [e.tolist() for e in embeddings]

    with open(FACES_FILE, "w") as f:
        json.dump(serializable, f)


def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return {}

    with open(PROCESSED_FILE, "r") as f:
        return json.load(f)


def save_processed(data):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(data, f, indent=2)
