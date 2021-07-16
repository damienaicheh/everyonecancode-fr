import os
import io
from fastapi import FastAPI, HTTPException, File, UploadFile
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from fastapi.responses import StreamingResponse


connection_string = os.environ['STORAGE_CONNECTIONSTRING']
service = BlobServiceClient.from_connection_string(conn_str=connection_string)

# Get a client to interact with a specific container - though it may not yet exist
container_client = service.get_container_client("images")

app = FastAPI()


@app.get("/images")
async def list_images():
    try:
        blobs = [b.name for b in container_client.list_blobs()]
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Container not found")
    return {"files": blobs}


@app.get("/images/{image_name}")
async def images(image_name):
    try:
        blob_container_client = container_client.get_blob_client(image_name)
        blob = blob_container_client.download_blob()
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=404, detail="Your picture was not found, just try to upload again 🤓")
    return StreamingResponse(blob.chunks())


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    container_client.upload_blob(
        file.filename, file.file, blob_type="BlockBlob", overwrite=True)
    return {"filename": file.filename}