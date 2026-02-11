import os
import cv2
from tqdm import tqdm
from face_engine import FaceEngine
from face_store import (
    load_faces,
    save_faces,
    load_processed,
    save_processed,
)

IMAGES_FOLDER = "images"
MAX_WIDTH = 800

engine = FaceEngine()
known_faces = load_faces()
processed = load_processed()

for filename in tqdm(os.listdir(IMAGES_FOLDER)):
    if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
        continue

    if filename in processed:
        continue

    path = os.path.join(IMAGES_FOLDER, filename)
    img = cv2.imread(path)

    # Resize for speed
    height, width = img.shape[:2]
    if width > MAX_WIDTH:
        scale = MAX_WIDTH / width
        img = cv2.resize(img, None, fx=scale, fy=scale)

    faces = engine.detect_faces(img)

    people_in_image = []

    for face in faces:
        embedding = face.embedding
        match = engine.match_face(embedding, known_faces)

        if match:
            print(f"[MATCHED] {filename} → {match}")
            people_in_image.append(match)
        else:
            print(f"[NEW FACE] in {filename}")
            name = input("Enter name: ").strip()

            if name not in known_faces:
                known_faces[name] = []

            known_faces[name].append(embedding)
            save_faces(known_faces)
            people_in_image.append(name)

    processed[filename] = people_in_image
    save_processed(processed)

print("\nIndexing complete.")
