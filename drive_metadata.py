def write_people_metadata(service, file_id, people_alias_list):
    service.files().update(
        fileId=file_id,
        body={
            "appProperties": {
                "people": ",".join(people_alias_list),
                "indexed": "true"
            }
        }
    ).execute()
