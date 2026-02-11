from insightface.app import FaceAnalysis
import numpy as np


class FaceEngine:
    def __init__(self):
        self.app = FaceAnalysis(providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0)

    def detect_faces(self, img):
        return self.app.get(img)

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def match_face(self, embedding, known_faces, threshold=0.65):
        best_match = None
        best_score = 0

        for canonical, info in known_faces.items():
            for known_embedding in info["embeddings"]:
                score = self.cosine_similarity(embedding, known_embedding)

                if score > best_score:
                    best_score = score
                    best_match = canonical

        if best_score > threshold:
            return best_match

        return None
