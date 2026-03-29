# fetch_drive_people_metadata.py

import pickle
from googleapiclient.discovery import build

# -------------------------------
# AUTH (uses existing token file)
# -------------------------------
def get_drive_service(token_path="token_drive_1.pickle"):
    with open(token_path, "rb") as token:
        creds = pickle.load(token)

    service = build("drive", "v3", credentials=creds)
    return service


# -------------------------------
# FETCH FILES FROM DRIVE
# -------------------------------
def fetch_files(service, folder_id=None):
    """
    Fetch files from Google Drive.

    Args:
        service: Drive API service
        folder_id (str): Optional folder ID

    Returns:
        list: Files list
    """
    query = "trashed=false"

    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(
        q=query,
        fields="files(id, name, appProperties)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        pageSize=1000
    ).execute()

    return results.get("files", [])


# -------------------------------
# EXTRACT PEOPLE METADATA
# -------------------------------
def extract_people(app_props):
    if not app_props:
        return []

    people_str = app_props.get("d","")

    if not people_str:
        return []

    return [p.strip() for p in people_str.split(",") if p.strip()]


# -------------------------------
# BUILD OUTPUT
# -------------------------------
def build_people_data(files):
    output = []

    for file in files:
        people = extract_people(file.get("appProperties", {}))

        output.append({
            "file_id": file.get("id"),
            "name": file.get("name"),
            "people": people
        })

    return output


# -------------------------------
# MAIN
# -------------------------------
def main():
    service = get_drive_service("token_drive_2.pickle")

    # 🔹 OPTIONAL: put folder ID here
   #folder_id = None
    folder_id = "1TOmHZ-tm1UpKpgbPwJOtcdXzpAwgsDJw"

    files = fetch_files(service, folder_id)

    people_data = build_people_data(files)

    # Print results
    for item in people_data:
        print(item)


if __name__ == "__main__":
    main()