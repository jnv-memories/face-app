from insightface.app import FaceAnalysis
import cv2

# Initialize InsightFace
app = FaceAnalysis(providers=["CPUExecutionProvider"])
app.prepare(ctx_id=0)

# Load image
img = cv2.imread("test.jpg")

faces = app.get(img)

print("Faces detected:", len(faces))

# Print face info
for i, face in enumerate(faces):
    print(f"Face {i+1}: bbox={face.bbox}, confidence={face.det_score:.2f}")
