from drive_auth import get_drive_service

service = get_drive_service()

results = service.files().list(
    pageSize=10,
    fields="files(id, name)"
).execute()

files = results.get('files', [])

for file in files:
    print(file['name'], file['id'])
