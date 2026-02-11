import json
import os
import numpy as np

FILE_NAME = "known_faces.json"

def load_faces():
    if not os.path.exists(FILE_NAME):
        return {}

    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    # convert lists back to numpy arrays
    for name in data:
        data[name] = [np.array(e) for e in data[name]]

    return data


def save_faces(face_dict):
    serializable = {}
    for name, embeddings in face_dict.items():
        serializable[name] = [e.tolist() for e in embeddings]

    with open(FILE_NAME, "w") as f:
        json.dump(serializable, f, indent=2)
