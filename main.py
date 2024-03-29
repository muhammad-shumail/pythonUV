import os
import uuid
from typing import List, Union

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


url = "https://jsonplaceholder.typicode.com/users/"
response = requests.get(url)

@app.get("/")
async def root():
    return response.json()


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.post("/items/")
async def create_item(item: Item):
    print(item)
    return item


obj = [{"name": "string", "price": 312313123.2, "is_offer": True}]


@app.get("/users/me")
async def read_user_me():
    return obj


UPLOAD_DIRECTORY = "uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@app.post("/uploadfiles/")
async def create_upload_files(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    files: List[UploadFile] = File(...),
):
    uploaded_files = []
    for file in files:
        myuuid = str(uuid.uuid4())
        contents = await file.read()

        # Validate file size (max size 1MB)
        if len(contents) > 1e6:  # 1e6 bytes = 1MB
            raise HTTPException(status_code=400, detail="File size exceeds limit")

        # Save file to disk
        file_path = os.path.join(UPLOAD_DIRECTORY, myuuid + "_" + file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)

        uploaded_files.append(
            {"filename": file.filename, "uuid": myuuid, "file_path": file_path}
        )

    data = {
        "uploaded_files": uploaded_files,
        "metadata": {"email": email, "name": name, "phone": phone},
    }
    return data


@app.get("/files/{file_uuid}")
async def read_file(file_uuid: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, file_uuid)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=file_path)



