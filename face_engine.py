from insightface.app import FaceAnalysis
import numpy as np

class FaceEngine:
    def __init__(self):
        self.app = FaceAnalysis(providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0)

    def detect_faces(self, img):
        return self.app.get(img)

    def match_face(self, embedding, known_faces, threshold=0.5):
        for name, embeddings in known_faces.items():
            for known_embedding in embeddings:
                similarity = np.dot(embedding, known_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(known_embedding)
                )

                if similarity > (1 - threshold):
                    return name

        return None
