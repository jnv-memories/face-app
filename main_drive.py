import cv2
import numpy as np
from tqdm import tqdm

from drive_auth import get_drive_service
from drive_fetch import list_files_in_folder, download_image
from drive_metadata import write_people_metadata
from face_engine import FaceEngine
from face_store import (
    load_faces,
    save_faces,
    load_processed,
    save_processed,
    load_videos,
    save_videos,
)

MAX_WIDTH = 800
AUTO_MERGE_THRESHOLD = 0.79


def resize_image(img):
    height, width = img.shape[:2]
    if width > MAX_WIDTH:
        scale = MAX_WIDTH / width
        img = cv2.resize(img, None, fx=scale, fy=scale)
    return img


def show_face_preview(img, faces, current_index):
    preview = img.copy()

    for i, face in enumerate(faces):
        bbox = face.bbox.astype(int)
        x1, y1, x2, y2 = bbox

        color = (255, 0, 0)
        thickness = 2

        if i == current_index:
            color = (0, 255, 0)
            thickness = 3

        cv2.rectangle(preview, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(
            preview,
            f"Face {i+1}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    cv2.imshow("Face Indexing - Type name in terminal", preview)
    cv2.waitKey(1)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def try_auto_merge(new_embedding, new_canonical, known_faces):
    """
    If new canonical embedding is very similar to existing canonical,
    merge automatically.
    """
    for canonical, info in known_faces.items():
        if canonical == new_canonical:
            continue

        for emb in info["embeddings"]:
            score = cosine_similarity(new_embedding, emb)
            if score > AUTO_MERGE_THRESHOLD:
                print(f"[AUTO MERGE] {new_canonical} → merged into {canonical}")
                return canonical

    return None


def build_metadata_string(canonicals, known_faces):
    if len(canonicals) > 3:
        first_names = [c.split()[0] for c in canonicals]
        return list(set(first_names))
    else:
        full_data = []
        for c in canonicals:
            full_data.extend(known_faces[c]["aliases"])
        return list(set(full_data))


def main():
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
    processed = load_processed()
    videos = load_videos()

    files = list_files_in_folder(service, folder_id)

    for file in tqdm(files):

        file_id = file["id"]
        name = file["name"]
        mime = file["mimeType"]

        if file_id in processed:
            continue

        if "video" in mime:
            videos[file_id] = name
            save_videos(videos)
            continue

        if "image" not in mime:
            continue

        print(f"\nProcessing: {name}")

        try:
            image_bytes = download_image(service, file_id)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            img = resize_image(img)
            faces = engine.detect_faces(img)

            if len(faces) == 0:
                processed[file_id] = []
                save_processed(processed)
                continue

            canonical_people = []

            for index, face in enumerate(faces):

                show_face_preview(img, faces, index)

                embedding = face.embedding
                match = engine.match_face(embedding, known_faces)

                if match:
                    print(f"[MATCHED] → {match}")
                    canonical_people.append(match)

                else:
                    print("[NEW FACE]")
                    user_input = input(
                        "Enter canonical full name (comma aliases allowed): "
                    ).strip()

                    aliases = [n.strip() for n in user_input.split(",")]
                    input_first_name = aliases[0].split()[0].lower()

                    found_canonical = None

                    for canonical_name, info in known_faces.items():

                        canonical_first = canonical_name.split()[0].lower()

                        # First-name match ONLY if full input is single word
                        if len(aliases[0].split()) == 1 and input_first_name == canonical_first:
                            found_canonical = canonical_name
                            break

                        # Exact alias match
                        if any(alias.lower() in [a.lower() for a in info["aliases"]] for alias in aliases):
                            found_canonical = canonical_name
                            break


                    if found_canonical:
                        known_faces[found_canonical]["embeddings"].append(embedding)
                        print(f"Added embedding to existing canonical: {found_canonical}")
                        canonical = found_canonical

                    else:
                        canonical = aliases[0]

                        # Create temporarily
                        known_faces[canonical] = {
                            "aliases": aliases,
                            "embeddings": [embedding],
                        }

                        # Try auto merge
                        merge_target = try_auto_merge(
                            embedding, canonical, known_faces
                        )

                        if merge_target:
                            known_faces[merge_target]["embeddings"].append(embedding)
                            known_faces[merge_target]["aliases"] = list(
                                set(
                                    known_faces[merge_target]["aliases"] + aliases
                                )
                            )
                            del known_faces[canonical]
                            canonical = merge_target
                        else:
                            print("Created new canonical entry.")

                    save_faces(known_faces)
                    canonical_people.append(canonical)

            cv2.destroyAllWindows()

            canonical_people = list(set(canonical_people))
            metadata_people = build_metadata_string(canonical_people, known_faces)

            write_people_metadata(service, file_id, metadata_people)

            processed[file_id] = metadata_people
            save_processed(processed)

        except Exception as e:
            print(f"Error processing {name}: {e}")
            continue

    print("\nFolder indexing complete.")


if __name__ == "__main__":
    main()
