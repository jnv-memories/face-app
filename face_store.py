import json
import os
import numpy as np

FACES_FILE = "known_faces.json"
PROCESSED_FILE = "processed_drive_files.json"
VIDEOS_FILE = "videos_found.json"


def load_faces():
    if not os.path.exists(FACES_FILE):
        return {}

    with open(FACES_FILE, "r") as f:
        data = json.load(f)

    for person in data:
        data[person]["embeddings"] = [
            np.array(e) for e in data[person]["embeddings"]
        ]

    return data


def save_faces(face_dict):
    serializable = {}

    for person, info in face_dict.items():
        serializable[person] = {
            "aliases": info["aliases"],
            "embeddings": [e.tolist() for e in info["embeddings"]],
        }

    with open(FACES_FILE, "w") as f:
        json.dump(serializable, f, indent=2)


def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return {}

    with open(PROCESSED_FILE, "r") as f:
        return json.load(f)


def save_processed(data):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_videos():
    if not os.path.exists(VIDEOS_FILE):
        return {}

    with open(VIDEOS_FILE, "r") as f:
        return json.load(f)


def save_videos(data):
    with open(VIDEOS_FILE, "w") as f:
        json.dump(data, f, indent=2)
