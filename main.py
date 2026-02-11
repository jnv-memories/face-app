import os
import cv2
from tqdm import tqdm
from face_engine import FaceEngine
from face_store import load_faces, save_faces

IMAGES_FOLDER = "images"

engine = FaceEngine()
known_faces = load_faces()

for filename in tqdm(os.listdir(IMAGES_FOLDER)):
    if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
        continue

    path = os.path.join(IMAGES_FOLDER, filename)
    img = cv2.imread(path)

    faces = engine.detect_faces(img)

    for face in faces:
        embedding = face.embedding

        match = engine.match_face(embedding, known_faces)

        if match:
            print(f"[MATCHED] {filename} → {match}")
        else:
            print(f"[NEW FACE] in {filename}")
            name = input("Enter name: ").strip()

            if name not in known_faces:
                known_faces[name] = []

            known_faces[name].append(embedding)
            save_faces(known_faces)
