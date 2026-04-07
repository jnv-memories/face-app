import cv2
import numpy as np
import json
import os
from tqdm import tqdm

from drive_auth import get_drive_service
from drive_fetch import list_files_in_folder, download_image
from face_engine import FaceEngine
from face_store import load_faces, save_faces
from drive_metadata import write_people_metadata

MAX_WIDTH = 800
PENDING_FILE = "pending_faces.json"


def resize_image(img):
    h, w = img.shape[:2]
    if w > MAX_WIDTH:
        scale = MAX_WIDTH / w
        img = cv2.resize(img, None, fx=scale, fy=scale)
    return img

def build_metadata_string(canonicals, known_faces):
    if len(canonicals) > 3:
        first_names = [c.split()[0] for c in canonicals]
        return list(set(first_names))
    else:
        full_data = []
        for c in canonicals:
            full_data.extend(known_faces[c]["aliases"])
        return list(set(full_data))
        
def sanitize_filename(name):
    name = os.path.splitext(name)[0]
    name = name.lower()
    return "".join(c if c.isalnum() else "_" for c in name)


def is_temp_name(name):

    return "_" in name and name.split("_")[-1].isdigit()


def load_pending():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    return {}


def save_pending(data):
    with open(PENDING_FILE, "w") as f:
        json.dump(data, f, indent=4)

def show_face_preview(img, faces, current_index):
    """
    Performance Boosted Preview: 
    Uses single window initialization and optimized drawing.
    """
    preview = img.copy()

    for i, face in enumerate(faces):
        x1, y1, x2, y2 = face.bbox.astype(int)
        
        # Highlight selected face in Green, others in Blue
        is_selected = (i == current_index)
        color = (0, 255, 0) if is_selected else (255, 0, 0)
        thickness = 3 if is_selected else 1

        cv2.rectangle(preview, (x1, y1), (x2, y2), color, thickness)
        
        label = f"Face {i+1}" + (" [Target]" if is_selected else "")
        cv2.putText(
            preview,
            label,
            (x1, max(y1 - 10, 20)), 
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA
        )

    cv2.imshow("Face Preview", preview)
    cv2.waitKey(1)


def fast_mode():
    print("\nSelect Drive Account:")
    print("1. Drive 1")
    print("2. Drive 2")
    print("3. Drive 3")
    print("4. Drive 4")

    choice = input("Enter choice (1-4): ").strip()
    account_name = f"drive_{choice}"

    service = get_drive_service(account_name)
    folder_id = input("Enter Drive Folder ID: ").strip()

    engine = FaceEngine()
    known_faces = load_faces()
    pending = load_pending()

    files = list_files_in_folder(service, folder_id)

    for file in tqdm(files):
        file_id = file["id"]
        name = file["name"]
        mime = file["mimeType"]

        # Skip 
        if file.get("appProperties", {}).get("d") in ["1", "2"]:
            continue

        if "image" not in mime:
            continue

        print(f"\nProcessing: {name}")

        try:
            image_bytes = download_image(service, file_id)
            img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            img = resize_image(img)

            faces = engine.detect_faces(img)

            if len(faces) == 0:
                service.files().update(
                    fileId=file_id,
                    body={"appProperties": {"d": "1"}}
                ).execute()
                continue

            unknown_names = []
            canonical_people = []

            base_name = sanitize_filename(name)

            for i, face in enumerate(faces):
                emb = face.embedding
                match = engine.match_face(emb, known_faces)

                if match:
                    print(f"[MATCHED] → {match}")

                    if is_temp_name(match):
                        unknown_names.append(match)
                    else:
                        canonical_people.append(match)

                    continue

                print("[NEW FACE]")

                temp_name = f"{base_name}_{i+1}"

                # Avoid duplicate entries
                if temp_name not in known_faces:
                    known_faces[temp_name] = {
                        "aliases": [temp_name],
                        "embeddings": [emb]
                    }
                else:
                    known_faces[temp_name]["embeddings"].append(emb)

                unknown_names.append(temp_name)

            save_faces(known_faces)
            canonical_people = list(set(canonical_people))

            if canonical_people:
                metadata_people = build_metadata_string(canonical_people, known_faces)

                try:
                    write_people_metadata(service, file_id, metadata_people)
                except Exception as e:
                    print(f"[Metadata Error] {e}")
            
            if unknown_names:
                pending[file_id] = {
                    "file_name": name,
                    "drive": account_name,
                    "folder_id": folder_id,
                    "unknown_faces": list(set(unknown_names))
                }

                service.files().update(
                    fileId=file_id,
                    body={"appProperties": {"d": "3"}}
                ).execute()

            else:
                service.files().update(
                    fileId=file_id,
                    body={"appProperties": {"d": "1"}}
                ).execute()

            save_pending(pending)

        except Exception as e:
            print(f"Error processing {name}: {e}")

    print("\nFast mode complete.")


def slow_mode():
    pending = load_pending()

    if not pending:
        print("No pending files.")
        return

    known_faces = load_faces()
    engine = FaceEngine()

    # 🔥 Initialize preview window (same as main)
    cv2.namedWindow("Face Preview", cv2.WINDOW_AUTOSIZE)

    for file_id, info in pending.items():
        print(f"\nProcessing pending: {info['file_name']}")

        service = get_drive_service(info["drive"])

        try:
            image_bytes = download_image(service, file_id)
            img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            img = resize_image(img)

            faces = engine.detect_faces(img)

            base_name = sanitize_filename(info["file_name"])

            if len(faces) == 0:
                service.files().update(
                    fileId=file_id,
                    body={"appProperties": {"d": "1"}}
                ).execute()
                continue

            for index, face in enumerate(faces):

                # 🔥 SHOW PREVIEW (same as main_drive.py)
                show_face_preview(img, faces, index)

                emb = face.embedding
                match = engine.match_face(emb, known_faces)

                # Skip real known faces
                if match and not is_temp_name(match):
                    print(f"[MATCHED] → {match}")
                    continue

                print("[NEW FACE - NEED NAME]")

                name_input = input(
                    "Enter canonical full name (comma aliases allowed): \n"
                    "(or press enter to skip)"
                ).strip()

                if name_input == "":
                    print("Skipped this face.")
                    continue

                aliases = [n.strip() for n in name_input.split(",")]
                canonical = aliases[0]

                # Merge into existing
                if canonical in known_faces:
                    known_faces[canonical]["embeddings"].append(emb)
                    known_faces[canonical]["aliases"] = list(
                        set(known_faces[canonical]["aliases"] + aliases)
                    )
                else:
                    known_faces[canonical] = {
                        "aliases": aliases,
                        "embeddings": [emb]
                    }

                # 🔥 REMOVE TEMP ENTRY
                if match and is_temp_name(match):
                    if match in known_faces:
                        del known_faces[match]

            save_faces(known_faces)

            # Close preview window after each file
            cv2.destroyAllWindows()

            # Mark completed
            service.files().update(
                fileId=file_id,
                body={"appProperties": {"d": "1"}}
            ).execute()

        except Exception as e:
            print(f"Error: {e}")

    save_pending({})
    print("\nSlow mode complete.")