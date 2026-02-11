from googleapiclient.http import MediaIoBaseDownload
import io


def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents"

    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType)"
    ).execute()

    return results.get('files', [])


def download_image(service, file_id):
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    file.seek(0)
    return file.read()
