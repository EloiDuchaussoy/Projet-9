import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

try:
    print("Azure Blob Storage Python quickstart sample")

    account_url = "https://ocp9edblob.blob.core.windows.net"
    default_credential = DefaultAzureCredential()

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)

    # Create a unique name for the container
    container_name = "dfrel"

    # Create the container
    container_client = blob_service_client.create_container(container_name)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="df_rel.csv")

    print("\nUploading to Azure Storage as blob:\n\t" + "df_rel.csv")

    # Upload the created file
    with open(file="df_rel.csv", mode="rb") as data:
        blob_client.upload_blob(data)

except Exception as ex:
    print('Exception:')
    print(ex)